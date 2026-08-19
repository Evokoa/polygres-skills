#!/usr/bin/env python3
"""Render one concise approval review from a Polygres setup manifest."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from validate_pipeline_plan import (
    PlanValidationError,
    approval_boundary,
    approval_digest,
    load_and_validate,
)


def render_review(plan: dict) -> str:
    actions = [
        action
        for action in plan.get("actions", [])
        if isinstance(action, dict) and action.get("enabled", True) is not False
    ]
    boundary = approval_boundary(plan)
    lines = [
        "# Polygres setup review",
        "",
        f"- Project: `{boundary['project_id'] or 'unresolved'}`",
        f"- Project mode: `{boundary['project_mode'] or 'standard'}`",
        f"- Source scope: {boundary['source_scope'] or 'not recorded'}",
        f"- Source system of record: {boundary['source_authority'] or 'not recorded'}",
        f"- Data egress: {', '.join(boundary['data_egress']) or 'none'}",
        f"- Destructive effects: {', '.join(boundary['destructive_actions']) or 'none'}",
        f"- Paid processing: {', '.join(boundary['paid_processing']) or 'none'}",
        f"- Approval digest: `{approval_digest(plan)}`",
        "",
        "## Planned actions",
        "",
    ]
    if boundary["project_mode"] == "synced":
        sync = plan.get("sync") if isinstance(plan.get("sync"), dict) else {}
        lines[6:6] = [
            f"- Selected sync tables: {', '.join(boundary['sync_selection']) or 'not recorded'}",
            f"- Source provider: {sync.get('provider', 'PostgreSQL')}",
            "- Managed replication resources: Polygres owns the filtered publication and slot",
            "- Write path: mutate the source database; the synced target is retrieval-only",
            (
                "- Reconfiguration: re-inspect the source; added or changed tables resync, "
                "and deselected tables stop syncing"
            ),
        ]
    if not actions:
        lines.append("None. The current plan contains only local or read-only work.")
    for action in actions:
        effect = action.get("effect", action.get("type", "remote mutation"))
        lines.extend(
            [
                f"- **{action.get('id', 'action')}**: {effect}",
                f"  - Target: {action.get('target', boundary['project_id'])}",
                f"  - Data egress: {action.get('data_egress', 'none')}",
            ]
        )
    embedding_options = plan.get("embedding_options")
    embedding = plan.get("embedding")
    embedding_enabled = (
        not isinstance(embedding, dict) or embedding.get("enabled", True) is not False
    )
    if embedding_enabled and isinstance(embedding_options, list) and embedding_options:
        recommended_id = plan.get("recommended_embedding_id")
        lines.extend(["", "## Embedding choice", ""])
        for option in embedding_options[:2]:
            if not isinstance(option, dict):
                continue
            label = " (recommended)" if option.get("id") == recommended_id else ""
            dimensions = option.get("dimensions", {})
            default_dimensions = (
                dimensions.get("default") if isinstance(dimensions, dict) else dimensions
            )
            lines.extend(
                [
                    f"- **{option.get('model', option.get('id', 'embedding'))}**{label}",
                    f"  - Location/provider: {option.get('category', 'unknown')} / "
                    f"{option.get('provider', 'unknown')}",
                    f"  - Dimensions: {default_dimensions or 'provider default'}",
                    f"  - Setup: {option.get('setup_action', 'use the recorded model contract')}",
                    f"  - Data egress: {option.get('data_egress', 'none')}",
                    f"  - Paid processing: {'yes' if option.get('paid_processing') else 'no'}",
                ]
            )
    lines.extend(
        [
            "",
            (
                "Reply `approve recommended` or select the other reviewed option. Either response "
                "selects the model and approves this setup."
                if embedding_enabled
                and isinstance(embedding_options, list)
                and len(embedding_options) > 1
                else "Approve once. Re-review only if a material boundary above changes."
            ),
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        review = render_review(load_and_validate(args.plan))
        if args.output:
            args.output.write_text(review, encoding="utf-8")
        else:
            print(review, end="")
    except (OSError, PlanValidationError) as error:
        print(f"review failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
