from __future__ import annotations

import copy
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

PACKAGE_ROOT = Path(__file__).parents[1]
SKILL_ROOT = PACKAGE_ROOT / "plugins" / "polygres" / "skills" / "polygres-data-pipeline"
SCRIPT_ROOT = SKILL_ROOT / "scripts"
ASSET_ROOT = SKILL_ROOT / "assets" / "python-pipeline"
EMBEDDING_CATALOG = SKILL_ROOT / "assets" / "embedding-models.json"


def _load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _plan() -> dict[str, Any]:
    return {
        "version": 2,
        "pipeline_id": "chat-memory",
        "name": "Chat memory",
        "state": "ready_for_review",
        "target": {"organization_id": "org_example", "project_id": "project_example"},
        "source": {
            "kind": "chat-export",
            "scope": "selected project conversations",
            "stable_id": {"field": "message_id", "strategy": "source"},
            "deletions": "propagate source tombstones",
        },
        "ownership": {"mode": "user", "field": "owner_id"},
        "schema": {
            "enabled": True,
            "mode": "create",
            "schema": "public",
            "table": "agent_memory",
            "columns": [
                {"name": "id", "type": "text", "nullable": False, "primary_key": True},
                {
                    "name": "owner_id",
                    "type": "text",
                    "nullable": False,
                    "primary_key": False,
                },
                {
                    "name": "content",
                    "type": "text",
                    "nullable": False,
                    "primary_key": False,
                },
                {
                    "name": "embedding",
                    "type": "vector",
                    "nullable": False,
                    "primary_key": False,
                },
            ],
        },
        "privacy": {
            "excluded_fields": [],
            "local_filtering": True,
            "retention": "delete derived data after source deletion",
        },
        "embedding": {
            "enabled": True,
            "location": "local",
            "provider": "ollama",
            "model": "embeddinggemma",
            "revision": "local-model-manifest",
            "dimensions": 768,
            "normalization": "l2",
            "document_input_format": "content",
            "query_input_format": "query text",
            "batching": "up to 16 records",
            "timeout_seconds": 30,
            "rate_limit": "local runtime limit",
            "credential_names": [],
            "endpoint_class": "loopback",
            "endpoint": "http://127.0.0.1:11434",
            "data_egress": "none",
            "cost": "",
        },
        "graph": {"enabled": False, "nodes": [], "edges": []},
        "context": {
            "enabled": True,
            "collection": "chat_memory",
            "source_schema": "public",
            "source_table": "agent_memory",
            "source_key_column": "id",
            "vector_column": "embedding",
            "text_column": "content",
        },
        "text": {"enabled": True, "columns": ["content"]},
        "sync": {
            "mode": "post-turn",
            "guarantee": "best-effort",
            "checkpoint": "state/checkpoint.sqlite3",
        },
        "capture_runtime": {
            "enabled": True,
            "command": "python3 capture.py",
            "interface": {
                "surface": "sdk",
                "operation": "project.rows.upsert",
                "reason": "post-turn stable-key capture",
                "documented": True,
            },
            "row_write_capability": "available",
        },
        "retrieval_runtime": {
            "enabled": True,
            "command": "python3 recall.py",
            "interface": {
                "surface": "sdk",
                "operation": "project.context.search",
                "reason": "per-prompt application recall",
                "documented": True,
            },
            "modes": ["semantic", "text"],
            "when": "meaningful-prompt",
            "limit": 5,
            "token_budget": 1600,
            "fallback": "continue without memory and report degraded mode",
        },
        "agent_integration": {
            "enabled": True,
            "target": "AGENTS.md",
            "capture_command": "python3 capture.py",
            "recall_command": "python3 recall.py",
            "guarantee": "best-effort",
        },
        "credentials": {
            "env_file": ".env",
            "required": ["POLYGRES_RUNTIME_URL", "POLYGRES_API_KEY"],
        },
        "actions": [
            {
                "id": "create-schema",
                "type": "schema-create",
                "target": "project_example/public.agent_memory",
                "effect": "create the memory table",
                "data_egress": "none",
                "reversibility": "reversible",
                "rollback": "drop only the newly created table after review",
                "requires_approval": True,
                "dependencies": [],
            },
            {
                "id": "configure-context",
                "type": "context-configure",
                "target": "project_example/chat_memory",
                "effect": "create the Context collection",
                "data_egress": "filtered records go to Polygres",
                "reversibility": "reversible",
                "rollback": "delete the new collection",
                "requires_approval": True,
                "dependencies": ["create-schema"],
            },
            {
                "id": "update-agent",
                "type": "agent-instructions",
                "target": "AGENTS.md",
                "effect": "add a managed capture and recall block",
                "data_egress": "none",
                "reversibility": "reversible",
                "rollback": "remove the managed block",
                "requires_approval": True,
                "dependencies": [],
            },
        ],
        "approval": {
            "status": "pending",
            "plan_digest": None,
            "project_id": "project_example",
            "source_scope": "selected project conversations",
            "action_ids": ["create-schema", "configure-context", "update-agent"],
        },
        "verification": {
            "claims": [
                {"capability": "local-filter", "status": "pending", "evidence": None},
                {"capability": "retrieval", "status": "pending", "evidence": None},
            ]
        },
    }


def test_skill_structure_and_reference_routing() -> None:
    skill = SKILL_ROOT / "SKILL.md"
    text = skill.read_text(encoding="utf-8")
    assert text.startswith("---\nname: polygres-data-pipeline\n")
    assert len(text.splitlines()) < 500
    assert (SKILL_ROOT / "agents" / "openai.yaml").is_file()
    references = {path.name for path in (SKILL_ROOT / "references").glob("*.md")}
    assert references == {
        "context-and-retrieval.md",
        "embedding-model-selection.md",
        "guided-interview.md",
        "pipeline-plan-contract.md",
        "pipeline-runtime.md",
        "schema-and-graph.md",
        "security-and-approvals.md",
        "source-chat-agents.md",
        "source-databases.md",
        "source-files-and-apis.md",
    }
    for reference in references:
        assert f"`references/{reference}`" in text


def test_skill_enforces_fast_path_embedding_and_credential_boundaries() -> None:
    text = " ".join(
        "\n".join(
            path.read_text(encoding="utf-8")
            for path in [
                SKILL_ROOT / "SKILL.md",
                *(SKILL_ROOT / "references").glob("*.md"),
            ]
        ).split()
    )
    for phrase in (
        "Ask one concise batch of questions only for critical facts",
        "Do not ask about optional components that are unnecessary",
        "check_embedding_device.py",
        "Polygres does not generate source or query embeddings",
        "Never read credential values",
        "cp .env.example .env",
        "documented rows Runtime API",
        "Never infer the endpoint",
        "public interface appropriate to each workload",
        "Keep the CLI for operator checks and manual recall",
        "at most one local recommendation and one hosted alternative",
        "Do not ask for a second approval",
    ):
        assert phrase in text


def test_skill_uses_an_adaptive_execution_path() -> None:
    skill_text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    all_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [SKILL_ROOT / "SKILL.md", *(SKILL_ROOT / "references").glob("*.md")]
    )
    normalized = " ".join(all_text.split())
    for phrase in (
        "Help me set up Polygres",
        "one bounded source sample",
        "Ask one concise batch of questions",
        "Do not force every setup",
        "one consolidated review",
        "A single memory table does not by itself justify graph",
        "scripts/update_agent_instructions.py",
        "project.rows",
        "CLI/SDK `0.3.0`",
    ):
        assert phrase in normalized

    for obsolete_instruction in (
        "Do not inspect more than 20",
        "use at most five discovery tool calls",
        "version 1 `plan.json`",
    ):
        assert obsolete_instruction not in skill_text


def test_pipeline_defaults_are_guidance_while_safety_boundaries_stay_firm() -> None:
    all_text = " ".join(
        "\n".join(
            path.read_text(encoding="utf-8")
            for path in [SKILL_ROOT / "SKILL.md", *(SKILL_ROOT / "references").glob("*.md")]
        ).split()
    )
    for phrase in (
        "decision guide, not a mandatory architecture or ordered checklist",
        "Numeric defaults are starting points",
        "Five to 20 records is a useful starting range, not a requirement",
        "self-references or reliably derived relationships may",
        "capture, recall, or both according to the integration",
        "Apply it to the active instruction file only after",
    ):
        assert phrase in all_text


def test_fully_vague_setup_asks_for_direction_before_inspection() -> None:
    all_text = " ".join(
        "\n".join(
            path.read_text(encoding="utf-8")
            for path in [
                SKILL_ROOT / "SKILL.md",
                SKILL_ROOT / "references" / "guided-interview.md",
            ]
        ).split()
    )
    for phrase in (
        "If the prompt identifies neither a source or inspectable context nor a desired outcome",
        "do not inspect, design, scaffold, or configure yet",
        "What would you like Polygres to do, and where is the relevant data?",
        "Begin when the answer identifies a source, an outcome, or both",
        "Contextual prompts",
        "skip this question and proceed immediately",
    ):
        assert phrase in all_text


def test_capability_question_returns_a_personalized_read_only_recommendation() -> None:
    text = " ".join((SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8").split())
    for phrase in (
        "What can I do with Polygres?",
        "personalized recommendation branch",
        "bounded, read-only checks",
        "leads with the most useful Polygres outcome for this project",
        "Do not return a generic feature list, create a plan, scaffold files, or mutate anything",
        "To proceed, reply: Set up the recommended Polygres pipeline",
        "Treat that reply or an equivalent acceptance as setup intent",
        "without repeating discovery unless the evidence is stale",
        "This acceptance starts setup; it is not mutation approval",
    ):
        assert phrase in text


def test_pipeline_guidance_distinguishes_row_only_from_context_replay() -> None:
    references = SKILL_ROOT / "references"
    for name in ("pipeline-runtime.md", "source-chat-agents.md", "source-databases.md"):
        text = " ".join((references / name).read_text(encoding="utf-8").lower().split())
        assert "row-only" in text
        assert "exact payload" in text
        assert "idempotency key" in text


def test_pipeline_routes_import_rows_api_context_and_deletion_by_workload() -> None:
    skill = " ".join((SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8").split())
    runtime = " ".join(
        (SKILL_ROOT / "references" / "pipeline-runtime.md")
        .read_text(encoding="utf-8")
        .split()
    )
    context = " ".join(
        (SKILL_ROOT / "references" / "context-and-retrieval.md")
        .read_text(encoding="utf-8")
        .split()
    )
    databases = " ".join(
        (SKILL_ROOT / "references" / "source-databases.md")
        .read_text(encoding="utf-8")
        .split()
    )

    assert "dataset or bounded backfill" in skill
    assert "one JSON object or runtime event" in skill
    assert "read-only `project.rows.validate(...)`" in runtime
    assert "POST /tables/{schema}/{table}/rows/validate" in runtime
    assert "POST /tables/{schema}/{table}/rows" in runtime
    assert "trusted server-side code" in runtime
    assert "256 KiB" in runtime and "60 writes per minute" in runtime
    assert "follow a successful import with approved existing-row point reconciliation" in runtime
    assert "CLI bulk import changes source rows only" in context
    assert "rows API has no delete mode" in databases
    assert "ROW_CONTEXT_IDEMPOTENCY_EXPIRED" in runtime


def test_plan_validator_accepts_a_complete_adaptive_plan() -> None:
    validator = _load_module("pipeline_plan_validator", SCRIPT_ROOT / "validate_pipeline_plan.py")
    assert validator.validate_plan(_plan())["pipeline_id"] == "chat-memory"


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        ("secret", "secret-value"),
        ("unresolved-project", "unresolved-project"),
        ("unavailable-interface", "interface-unavailable"),
        ("stale-approval", "stale-approval"),
        ("unverified-operational", "unverified-operational-claim"),
    ],
)
def test_plan_linter_blocks_only_material_safety_failures(mutation: str, expected: str) -> None:
    validator = _load_module(
        f"pipeline_plan_validator_{mutation}", SCRIPT_ROOT / "validate_pipeline_plan.py"
    )
    plan = _plan()
    if mutation == "secret":
        plan["credentials"]["api_key"] = "not-a-real-value"
    elif mutation == "unresolved-project":
        plan["target"] = {}
    elif mutation == "unavailable-interface":
        plan["capture_runtime"]["interface"]["available"] = False
    elif mutation == "stale-approval":
        plan["approval"] = {"status": "approved", "boundary_digest": "sha256:stale"}
    elif mutation == "unverified-operational":
        plan["state"] = "operational"
    result = validator.lint_plan(plan)
    assert expected in {blocker["code"] for blocker in result.blockers}


def test_plan_linter_warns_without_blocking_incomplete_optional_details() -> None:
    validator = _load_module(
        "pipeline_permissive_validator", SCRIPT_ROOT / "validate_pipeline_plan.py"
    )
    plan = {"name": "Small local setup"}
    result = validator.lint_plan(plan)
    assert result.ok
    assert result.warnings


def test_scaffolder_creates_a_secret_free_setup_pack(tmp_path: Path) -> None:
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(json.dumps(_plan()), encoding="utf-8")
    destination = tmp_path / "generated"
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_ROOT / "scaffold_pipeline.py"),
            str(plan_path),
            str(destination),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert not (destination / ".env").exists()
    assert (destination / ".env.example").read_text() == (
        "POLYGRES_RUNTIME_URL=\nPOLYGRES_API_KEY=\n"
    )
    assert ".env\n" in (destination / ".gitignore").read_text()
    assert "vector(768)" in (destination / "schema.sql").read_text()
    assert (
        json.loads((destination / "capture-runtime.json").read_text()) == _plan()["capture_runtime"]
    )
    readme = (destination / "README.md").read_text()
    assert "Selected components" in readme
    assert "per-record capture" in readme
    assert "create-schema" in (destination / "REVIEW.md").read_text()
    assert "update-agent" in (destination / "REVIEW.md").read_text()
    assert (destination / "embedding-models.json").is_file()
    assert (destination / "scripts" / "recommend_embedding_models.py").is_file()
    assert (destination / "scripts" / "check_env.py").is_file()
    assert (destination / "scripts" / "check_embedding_device.py").is_file()
    assert (destination / "scripts" / "update_agent_instructions.py").is_file()
    assert not (destination / "graph.json").exists()
    for path in destination.rglob("*"):
        if path.is_file():
            assert "not-a-real-value" not in path.read_text(encoding="utf-8")

    requirements_path = destination / "embedding-requirements.json"
    requirements_path.write_text(
        json.dumps({"deployment_preference": "hosted", "languages": ["en"]}),
        encoding="utf-8",
    )
    device_path = destination / "device.json"
    device_path.write_text(json.dumps({"memory_gib": 8, "disk_free_gib": 20}), encoding="utf-8")
    recommendation = subprocess.run(
        [
            sys.executable,
            str(destination / "scripts" / "recommend_embedding_models.py"),
            "--requirements",
            str(requirements_path),
            "--device",
            str(device_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert recommendation.returncode == 0, recommendation.stderr
    assert json.loads(recommendation.stdout)["recommended"]["category"] == "hosted"

    second = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_ROOT / "scaffold_pipeline.py"),
            str(plan_path),
            str(destination),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert second.returncode == 1
    assert "destination already exists" in second.stderr


def test_minimal_plan_omits_unselected_components(tmp_path: Path) -> None:
    plan = _plan()
    for component in (
        "schema",
        "embedding",
        "context",
        "text",
        "graph",
        "sync",
        "capture_runtime",
        "retrieval_runtime",
        "agent_integration",
        "credentials",
    ):
        plan.pop(component, None)
    plan["actions"] = []
    plan["approval"] = {
        "status": "not-required",
        "plan_digest": None,
        "project_id": "project_example",
        "source_scope": "selected project conversations",
        "action_ids": [],
    }
    plan["state"] = "operational"
    plan["verification"] = {
        "claims": [{"capability": "important-path", "status": "passed", "evidence": "sample read"}]
    }
    plan_path = tmp_path / "minimal.json"
    plan_path.write_text(json.dumps(plan), encoding="utf-8")
    destination = tmp_path / "minimal"
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_ROOT / "scaffold_pipeline.py"),
            str(plan_path),
            str(destination),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert not (destination / "schema.sql").exists()
    assert not (destination / ".env.example").exists()
    assert not (destination / "lib").exists()
    assert not (destination / "embedding-models.json").exists()
    assert not (destination / "scripts" / "recommend_embedding_models.py").exists()
    assert not (destination / "scripts" / "check_env.py").exists()
    assert not (destination / "scripts" / "check_embedding_device.py").exists()
    assert not (destination / "scripts" / "update_agent_instructions.py").exists()
    assert (destination / "scripts" / "render_pipeline_review.py").is_file()
    assert (destination / "scripts" / "validate_pipeline_plan.py").is_file()


def test_disabled_components_create_no_files_or_review_effects(tmp_path: Path) -> None:
    validator = _load_module(
        "pipeline_disabled_component_validator", SCRIPT_ROOT / "validate_pipeline_plan.py"
    )
    plan = {
        "name": "Explicitly minimal",
        "target": {},
        "source": {"scope": "one local file"},
        "embedding": {"enabled": False},
        "graph": {"enabled": False},
        "sync": {"enabled": False},
        "capture_runtime": {"enabled": False},
        "agent_integration": {"enabled": False},
        "embedding_options": [
            {
                "provider": "openai",
                "data_egress": "filtered text goes to OpenAI",
                "paid_processing": True,
            }
        ],
        "actions": [
            {
                "id": "unused-schema",
                "type": "schema-create",
                "enabled": False,
                "data_egress": "none",
            }
        ],
    }
    assert validator.lint_plan(plan).ok
    assert validator.approval_boundary(plan)["data_egress"] == []
    plan_path = tmp_path / "disabled.json"
    plan_path.write_text(json.dumps(plan), encoding="utf-8")
    destination = tmp_path / "disabled"
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_ROOT / "scaffold_pipeline.py"),
            str(plan_path),
            str(destination),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "unused-schema" not in (destination / "REVIEW.md").read_text(encoding="utf-8")
    for name in (
        "embedding.json",
        "graph.json",
        "sync.json",
        "capture-runtime.json",
        "agent-integration.json",
        "embedding-models.json",
    ):
        assert not (destination / name).exists()
    assert not (destination / "lib").exists()


def test_validator_accepts_user_selected_hosted_embeddings() -> None:
    validator = _load_module("pipeline_hosted_validator", SCRIPT_ROOT / "validate_pipeline_plan.py")
    plan = _plan()
    plan["embedding"].update(
        {
            "location": "hosted",
            "provider": "openai",
            "model": "text-embedding-example",
            "revision": "provider-version",
            "credential_names": ["OPENAI_API_KEY"],
            "endpoint_class": "hosted-https",
            "endpoint": "https://api.openai.com/v1/embeddings",
            "data_egress": "filtered content is sent to OpenAI",
            "cost": "provider usage charges",
        }
    )
    assert validator.validate_plan(plan)["embedding"]["provider"] == "openai"


def test_approval_digest_invalidates_changed_actions() -> None:
    validator = _load_module("pipeline_digest_validator", SCRIPT_ROOT / "validate_pipeline_plan.py")
    plan = _plan()
    plan["approval"]["status"] = "approved"
    plan["approval"]["boundary_digest"] = validator.approval_digest(plan)
    plan["approval"].pop("plan_digest", None)
    validator.validate_plan(plan)
    plan["actions"][0]["effect"] = "create a different table"
    validator.validate_plan(plan)
    plan["target"]["project_id"] = "another-project"
    with pytest.raises(validator.PlanValidationError, match="approval no longer matches"):
        validator.validate_plan(plan)


def test_approval_digest_tracks_only_material_review_boundaries() -> None:
    validator = _load_module(
        "pipeline_material_boundary_validator", SCRIPT_ROOT / "validate_pipeline_plan.py"
    )
    approved = _plan()
    approved["approval"] = {
        "status": "approved",
        "boundary_digest": validator.approval_digest(approved),
    }
    changes = (
        lambda plan: plan["source"].update(scope="all conversations"),
        lambda plan: plan["actions"][0].update(data_egress="records leave the device"),
        lambda plan: plan["actions"][0].update(destructive=True),
        lambda plan: plan["actions"][0].update(paid_processing=True),
    )
    for change in changes:
        changed = copy.deepcopy(approved)
        change(changed)
        assert "stale-approval" in {
            blocker["code"] for blocker in validator.lint_plan(changed).blockers
        }

    harmless = copy.deepcopy(approved)
    harmless["actions"][0]["rollback"] = "use a different harmless local command"
    assert validator.lint_plan(harmless).ok


def test_reviewed_embedding_alternative_is_covered_by_one_approval() -> None:
    validator = _load_module("validate_pipeline_plan", SCRIPT_ROOT / "validate_pipeline_plan.py")
    renderer = _load_module(
        "pipeline_embedding_review_renderer", SCRIPT_ROOT / "render_pipeline_review.py"
    )
    plan = _plan()
    plan["embedding_options"] = [
        {
            "id": "qwen3-embedding-0.6b",
            "category": "local",
            "provider": "ollama",
            "model": "qwen3-embedding:0.6b",
            "dimensions": {"default": 1024},
            "setup_action": "download the pinned 639 MB model",
            "data_egress": "none",
            "paid_processing": False,
        },
        {
            "id": "openai-text-embedding-3-small",
            "category": "hosted",
            "provider": "openai",
            "model": "text-embedding-3-small",
            "dimensions": {"default": 1536},
            "setup_action": "set OPENAI_API_KEY locally",
            "data_egress": "filtered embedding inputs are sent to openai",
            "paid_processing": True,
        },
    ]
    plan["recommended_embedding_id"] = "qwen3-embedding-0.6b"
    digest = validator.approval_digest(plan)
    review = renderer.render_review(plan)
    assert "qwen3-embedding:0.6b** (recommended)" in review
    assert "text-embedding-3-small" in review
    assert "selects the model and approves this setup" in review

    plan["approval"] = {"status": "approved", "boundary_digest": digest}
    plan["embedding"].update(
        {
            "location": "hosted",
            "provider": "openai",
            "model": "text-embedding-3-small",
            "data_egress": "filtered embedding inputs are sent to openai",
            "cost": "provider usage charges",
        }
    )
    assert validator.lint_plan(plan).ok


def test_agent_instruction_update_is_idempotent_and_reversible(tmp_path: Path) -> None:
    updater = SCRIPT_ROOT / "update_agent_instructions.py"
    instructions = tmp_path / "AGENTS.md"
    instructions.write_text("# Existing\n\nKeep this text.\n", encoding="utf-8")
    command = [
        sys.executable,
        str(updater),
        str(instructions),
        "--capture-command",
        "python3 capture.py",
        "--recall-command",
        "python3 recall.py",
    ]
    assert subprocess.run(command, check=False).returncode == 0
    once = instructions.read_text(encoding="utf-8")
    assert subprocess.run(command, check=False).returncode == 0
    assert instructions.read_text(encoding="utf-8") == once
    assert once.count("<!-- polygres-memory:start -->") == 1
    assert "Keep this text." in once
    assert (
        subprocess.run(
            [sys.executable, str(updater), str(instructions), "--remove"], check=False
        ).returncode
        == 0
    )
    assert "polygres-memory" not in instructions.read_text(encoding="utf-8")


def test_agent_instruction_update_supports_recall_without_capture(tmp_path: Path) -> None:
    updater = SCRIPT_ROOT / "update_agent_instructions.py"
    instructions = tmp_path / "AGENTS.md"
    result = subprocess.run(
        [
            sys.executable,
            str(updater),
            str(instructions),
            "--recall-command",
            "python3 recall.py",
            "--recall-when",
            "When the agent decides memory would help",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    text = instructions.read_text(encoding="utf-8")
    assert "When the agent decides memory would help" in text
    assert "python3 recall.py" in text
    assert "Treat capture as" not in text


def test_env_check_never_returns_values(tmp_path: Path) -> None:
    checker = _load_module("pipeline_env_check", SCRIPT_ROOT / "check_env.py")
    env_file = tmp_path / ".env"
    env_file.write_text("POLYGRES_API_KEY=private-test-value\nEMPTY=\n", encoding="utf-8")
    if os.name == "posix":
        env_file.chmod(0o600)
    report, ready = checker.check_required(env_file, ["POLYGRES_API_KEY", "EMPTY"])
    serialized = json.dumps(report)
    assert "private-test-value" not in serialized
    assert report["required"] == {"EMPTY": "empty", "POLYGRES_API_KEY": "present"}
    assert ready is False


def test_device_classification_uses_discovered_local_options() -> None:
    device = _load_module("pipeline_device_check", SCRIPT_ROOT / "check_embedding_device.py")
    facts = device.DeviceFacts(
        system="Linux",
        architecture="x86_64",
        python_version="3.12.0",
        memory_gib=16.0,
        memory_available_gib=12.0,
        disk_free_gib=100.0,
        accelerators=("Example GPU (8192 MiB)",),
        commands={"ollama": "ollama", "llama_server": None},
        python_modules={"sentence_transformers": False, "onnxruntime": False},
        ollama_models=("embeddinggemma:latest",),
        ollama_model_sizes={"embeddinggemma:latest": 622_000_000},
        ollama_version="0.11.4",
        llama_model=None,
        onnx_model=None,
    )
    options = {option["provider"]: option for option in device.classify_options(facts)}
    assert options["ollama"]["status"] == "ready"
    assert options["sentence-transformers"]["status"] == "available-after-setup"
    assert options["none"]["status"] == "ready"


def _device_report(*, memory: float = 16.0, installed: list[str] | None = None) -> dict[str, Any]:
    return {
        "memory_gib": memory,
        "memory_available_gib": memory,
        "disk_free_gib": 100.0,
        "commands": {"ollama": "ollama", "llama_server": None},
        "python_modules": {"sentence_transformers": False, "onnxruntime": False},
        "ollama_models": installed or [],
    }


def test_embedding_recommender_shows_one_local_and_one_hosted_path() -> None:
    recommender = _load_module(
        "pipeline_embedding_recommender", SCRIPT_ROOT / "recommend_embedding_models.py"
    )
    catalog = json.loads(EMBEDDING_CATALOG.read_text(encoding="utf-8"))
    report = recommender.recommend(
        catalog,
        {
            "deployment_preference": "unknown",
            "languages": ["en", "zh"],
            "max_chunk_tokens": 1500,
        },
        _device_report(),
    )
    assert report["status"] == "ready"
    assert report["preference_resolved"] is False
    assert report["recommended"]["category"] == "local"
    assert report["recommended"]["model"] == "qwen3-embedding:0.6b"
    assert report["alternative"]["category"] == "hosted"
    assert report["alternative"]["model"] == "text-embedding-3-small"


def test_embedding_recommender_respects_preference_and_processing_boundary() -> None:
    recommender = _load_module(
        "pipeline_embedding_recommender_boundaries",
        SCRIPT_ROOT / "recommend_embedding_models.py",
    )
    catalog = json.loads(EMBEDDING_CATALOG.read_text(encoding="utf-8"))
    hosted = recommender.recommend(
        catalog,
        {"deployment_preference": "hosted", "languages": ["en"]},
        _device_report(memory=1.0),
    )
    assert hosted["preference_resolved"] is True
    assert hosted["recommended"]["category"] == "hosted"
    assert hosted["alternative"] is None

    local_only = recommender.recommend(
        catalog,
        {
            "deployment_preference": "unknown",
            "languages": ["en"],
            "external_processing_allowed": False,
        },
        _device_report(),
    )
    assert local_only["recommended"]["category"] == "local"
    assert local_only["alternative"] is None


def test_embedding_recommender_prefers_installed_and_filters_requirements() -> None:
    recommender = _load_module(
        "pipeline_embedding_recommender_requirements",
        SCRIPT_ROOT / "recommend_embedding_models.py",
    )
    catalog = json.loads(EMBEDDING_CATALOG.read_text(encoding="utf-8"))
    installed = recommender.recommend(
        catalog,
        {"deployment_preference": "local", "languages": ["en"]},
        _device_report(installed=["nomic-embed-text:v1.5"]),
    )
    assert installed["recommended"]["model"] == "nomic-embed-text:v1.5"
    assert installed["recommended"]["installed"] is True

    lightweight = recommender.recommend(
        catalog,
        {"deployment_preference": "local", "languages": ["en"]},
        _device_report(memory=1.75),
    )
    assert lightweight["recommended"]["model"] == "BAAI/bge-small-en-v1.5"

    code = recommender.recommend(
        catalog,
        {
            "deployment_preference": "hosted",
            "languages": ["en"],
            "contains_code": True,
            "max_chunk_tokens": 16000,
        },
        _device_report(),
    )
    assert code["recommended"]["model"] == "voyage-code-3"


def test_embedding_catalog_has_pinned_aliases_and_primary_sources() -> None:
    catalog = json.loads(EMBEDDING_CATALOG.read_text(encoding="utf-8"))
    assert catalog["verified_at"] == "2026-08-14"
    for model in [*catalog["local"], *catalog["hosted"]]:
        assert model["sources"]
        assert all(source.startswith("https://") for source in model["sources"])
        assert all("latest" not in alias for alias in model.get("runtime_aliases", []))


def test_local_embedding_adapter_rejects_external_hosts_and_wrong_dimensions() -> None:
    embeddings = _load_module("pipeline_local_embeddings", ASSET_ROOT / "local_embeddings.py")
    external = embeddings.EmbeddingConfig(
        provider="local-http",
        model="example",
        revision="one",
        dimensions=2,
        normalization="none",
        endpoint="https://example.com",
    )
    with pytest.raises(embeddings.LocalEmbeddingError, match="loopback"):
        embeddings.create_provider(external)

    local = embeddings.EmbeddingConfig(
        provider="ollama",
        model="example",
        revision="one",
        dimensions=2,
        normalization="none",
        endpoint="http://127.0.0.1:11434",
    )
    with pytest.raises(embeddings.LocalEmbeddingError, match="wrong dimensions"):
        embeddings._validate_vectors([[1.0]], expected_count=1, config=local)


def test_checkpoint_ledger_is_idempotent_and_detects_revision_reuse(tmp_path: Path) -> None:
    ledger_module = _load_module("pipeline_checkpoint_ledger", ASSET_ROOT / "checkpoint_ledger.py")
    with ledger_module.CheckpointLedger(tmp_path / "state" / "ledger.sqlite3") as ledger:
        assert ledger.begin(
            source_namespace="chat",
            source_id="message-1",
            source_revision="one",
            content_hash="hash-one",
        )
        ledger.mark_succeeded("chat", "message-1", "one")
        assert not ledger.begin(
            source_namespace="chat",
            source_id="message-1",
            source_revision="one",
            content_hash="hash-one",
        )
        with pytest.raises(ValueError, match="reused"):
            ledger.begin(
                source_namespace="chat",
                source_id="message-1",
                source_revision="one",
                content_hash="different-hash",
            )
        assert ledger.counts()["succeeded"] == 1
