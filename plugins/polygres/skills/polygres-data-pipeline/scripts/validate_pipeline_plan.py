#!/usr/bin/env python3
"""Quietly lint an internal Polygres setup plan for material safety issues."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REMOTE_ACTION_TYPES = {
    "schema-create",
    "schema-alter",
    "bulk-import",
    "row-write",
    "context-configure",
    "text-configure",
    "graph-configure",
    "deploy",
    "backfill",
}
DESTRUCTIVE_ACTION_TYPES = {"delete", "replace", "drop", "revoke", "truncate"}
SECRET_KEYS = {"password", "api_key", "access_token", "secret", "token", "database_url"}
ENV_NAME = re.compile(r"^[A-Z_][A-Z0-9_]*$")
SECRET_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"[a-z][a-z0-9+.-]*://[^\s/:]+:[^\s@]+@", re.IGNORECASE),
    re.compile(r"\b(?:sk|pgs|token)[_-][A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),
)


@dataclass(frozen=True)
class LintResult:
    blockers: tuple[dict[str, str], ...]
    warnings: tuple[dict[str, str], ...]

    @property
    def ok(self) -> bool:
        return not self.blockers

    def as_dict(self) -> dict[str, Any]:
        return {"ok": self.ok, "blockers": list(self.blockers), "warnings": list(self.warnings)}


class PlanValidationError(ValueError):
    def __init__(self, blockers: tuple[dict[str, str], ...]) -> None:
        self.blockers = blockers
        super().__init__("; ".join(f"{item['path']}: {item['message']}" for item in blockers))


def _issue(code: str, path: str, message: str) -> dict[str, str]:
    return {"code": code, "path": path, "message": message}


def _actions(plan: dict[str, Any]) -> list[dict[str, Any]]:
    value = plan.get("actions", [])
    return (
        [
            item
            for item in value
            if isinstance(item, dict) and item.get("enabled", True) is not False
        ]
        if isinstance(value, list)
        else []
    )


def _is_remote(action: dict[str, Any]) -> bool:
    return bool(
        action.get("remote_mutation") is True
        or action.get("scope") == "remote"
        or action.get("type") in REMOTE_ACTION_TYPES
    )


def _is_destructive(action: dict[str, Any]) -> bool:
    text = " ".join(str(action.get(key, "")) for key in ("type", "effect")).casefold()
    return bool(
        action.get("destructive") is True or any(word in text for word in DESTRUCTIVE_ACTION_TYPES)
    )


def approval_boundary(plan: dict[str, Any]) -> dict[str, Any]:
    actions = _actions(plan)
    project_id = (
        plan.get("target", {}).get("project_id") if isinstance(plan.get("target"), dict) else None
    )
    source_scope = (
        plan.get("source", {}).get("scope") if isinstance(plan.get("source"), dict) else None
    )
    egress = sorted(
        {
            str(action["data_egress"])
            for action in actions
            if action.get("data_egress") not in (None, "", "none")
        }
    )
    destructive = sorted(
        str(action.get("id") or action.get("effect") or action.get("type"))
        for action in actions
        if _is_destructive(action)
    )
    paid = sorted(
        str(action.get("id") or action.get("effect") or action.get("type"))
        for action in actions
        if action.get("paid_processing") is True
    )
    embedding_options = plan.get("embedding_options")
    embedding = plan.get("embedding")
    embedding_enabled = (
        not isinstance(embedding, dict) or embedding.get("enabled", True) is not False
    )
    reviewed_options = (
        [option for option in embedding_options if isinstance(option, dict)]
        if embedding_enabled and isinstance(embedding_options, list)
        else []
    )
    if reviewed_options:
        for option in reviewed_options:
            data_egress = option.get("data_egress")
            if data_egress not in (None, "", "none"):
                egress.append(str(data_egress))
            if option.get("paid_processing") is True:
                paid.append(f"embedding:{option.get('provider', option.get('id', 'hosted'))}")
    else:
        if (
            isinstance(embedding, dict)
            and embedding.get("enabled")
            and embedding.get("location") == "hosted"
        ):
            cost = str(embedding.get("cost", "")).strip().casefold()
            if cost not in {"", "none", "free"}:
                paid.append(f"embedding:{embedding.get('provider', 'hosted')}")
            data_egress = embedding.get("data_egress")
            if data_egress not in (None, "", "none"):
                egress.append(str(data_egress))
    return {
        "project_id": project_id,
        "source_scope": source_scope,
        "data_egress": sorted(set(egress)),
        "destructive_actions": sorted(set(destructive)),
        "paid_processing": sorted(set(paid)),
    }


def approval_digest(plan: dict[str, Any]) -> str:
    payload = json.dumps(approval_boundary(plan), sort_keys=True, separators=(",", ":")).encode()
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def plan_digest(plan: dict[str, Any]) -> str:
    """Compatibility alias: approval intentionally covers only material boundaries."""
    return approval_digest(plan)


def _scan_secrets(value: Any, path: str, blockers: list[dict[str, str]]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            key_is_secret = str(key).casefold() in SECRET_KEYS
            env_reference = isinstance(child, str) and ENV_NAME.fullmatch(child) is not None
            if key_is_secret and child not in (None, "") and not env_reference:
                blockers.append(
                    _issue(
                        "secret-value",
                        child_path,
                        "store an environment-variable name, not a secret value",
                    )
                )
            _scan_secrets(child, child_path, blockers)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _scan_secrets(child, f"{path}[{index}]", blockers)
    elif isinstance(value, str) and any(pattern.search(value) for pattern in SECRET_PATTERNS):
        blockers.append(
            _issue("secret-value", path, "appears to contain a credential or private key")
        )


def _capability_available(plan: dict[str, Any], interface: dict[str, Any]) -> bool | None:
    if isinstance(interface.get("available"), bool):
        return interface["available"]
    capability = interface.get("capability")
    capabilities = plan.get("capabilities")
    if isinstance(capability, str) and isinstance(capabilities, dict):
        value = capabilities.get(capability)
        if isinstance(value, bool):
            return value
        if isinstance(value, dict) and isinstance(value.get("available"), bool):
            return value["available"]
    return None


def _interfaces(value: Any, path: str = "plan") -> list[tuple[str, dict[str, Any]]]:
    found: list[tuple[str, dict[str, Any]]] = []
    if isinstance(value, dict):
        if "surface" in value and "operation" in value:
            found.append((path, value))
        for key, child in value.items():
            found.extend(_interfaces(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(_interfaces(child, f"{path}[{index}]"))
    return found


def _important_path_tested(plan: dict[str, Any]) -> bool:
    verification = plan.get("verification")
    if not isinstance(verification, dict):
        return False
    important = verification.get("important_path")
    if isinstance(important, dict):
        return important.get("status") in {"passed", "tested"} and bool(important.get("evidence"))
    claims = verification.get("claims")
    if isinstance(claims, list):
        return any(
            isinstance(claim, dict)
            and claim.get("capability") in {"important-path", "vertical-slice", "end-to-end"}
            and claim.get("status") in {"passed", "tested"}
            and bool(claim.get("evidence"))
            for claim in claims
        )
    return False


def lint_plan(plan: Any) -> LintResult:
    blockers: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    if not isinstance(plan, dict):
        return LintResult((_issue("invalid-plan", "plan", "must be a JSON object"),), ())

    actions = _actions(plan)
    remote_actions = [action for action in actions if _is_remote(action)]
    target = plan.get("target")
    project_id = target.get("project_id") if isinstance(target, dict) else None
    if remote_actions and not project_id:
        blockers.append(
            _issue(
                "unresolved-project",
                "target.project_id",
                "resolve a Polygres project before any remote mutation",
            )
        )

    _scan_secrets(plan, "plan", blockers)

    approval = plan.get("approval")
    if isinstance(approval, dict) and approval.get("status") == "approved":
        recorded = approval.get("boundary_digest") or approval.get("plan_digest")
        if recorded != approval_digest(plan):
            blockers.append(
                _issue(
                    "stale-approval",
                    "approval",
                    "approval no longer matches a material review boundary",
                )
            )
    elif remote_actions:
        warnings.append(
            _issue(
                "approval-pending",
                "approval",
                "show one concise mutation review before applying remote actions",
            )
        )

    for path, interface in _interfaces(plan):
        available = _capability_available(plan, interface)
        if available is False:
            blockers.append(
                _issue(
                    "interface-unavailable",
                    path,
                    f"{interface.get('operation')} is unavailable according to capability evidence",
                )
            )
        elif available is None:
            warnings.append(
                _issue(
                    "capability-unverified", path, "verify this public interface before using it"
                )
            )

    if plan.get("state") == "operational" and not _important_path_tested(plan):
        blockers.append(
            _issue(
                "unverified-operational-claim",
                "state",
                "important path needs passing evidence before claiming operational",
            )
        )

    if not isinstance(plan.get("source"), dict) or not plan.get("source", {}).get("scope"):
        warnings.append(
            _issue("source-scope-missing", "source.scope", "infer a bounded scope before review")
        )
    if not actions:
        warnings.append(_issue("no-actions", "actions", "no setup actions are recorded"))
    return LintResult(tuple(blockers), tuple(warnings))


def validate_plan(plan: Any) -> dict[str, Any]:
    result = lint_plan(plan)
    if result.blockers:
        raise PlanValidationError(result.blockers)
    return plan


def load_and_lint(path: Path) -> tuple[dict[str, Any], LintResult]:
    plan = json.loads(path.read_text(encoding="utf-8"))
    return plan, lint_plan(plan)


def load_and_validate(path: Path) -> dict[str, Any]:
    plan, result = load_and_lint(path)
    if result.blockers:
        raise PlanValidationError(result.blockers)
    return plan


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--print-digest", action="store_true")
    args = parser.parse_args(argv)
    try:
        plan, result = load_and_lint(args.plan)
    except (OSError, json.JSONDecodeError) as error:
        result = LintResult((_issue("invalid-plan", "plan", str(error)),), ())
        plan = {}
    if args.print_digest and result.ok:
        print(approval_digest(plan))
    else:
        print(json.dumps(result.as_dict(), indent=2, sort_keys=True))
    return 1 if result.blockers else 0


if __name__ == "__main__":
    raise SystemExit(main())
