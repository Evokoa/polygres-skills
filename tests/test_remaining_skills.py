from __future__ import annotations

import json
import re
from pathlib import Path

PACKAGE_ROOT = Path(__file__).parents[1]
PLUGIN_ROOT = PACKAGE_ROOT / "plugins" / "polygres"
PACKAGE_VERSION = (PACKAGE_ROOT / "VERSION").read_text().strip()
SKILLS_ROOT = PLUGIN_ROOT / "skills"
DESIGN_ROOT = SKILLS_ROOT / "polygres-retrieval-design"
TROUBLESHOOTING_ROOT = SKILLS_ROOT / "polygres-troubleshooting"


def _frontmatter(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "---"
    return lines[1 : lines.index("---", 1)]


def _all_skill_text(root: Path) -> str:
    paths = [root / "SKILL.md", *(root / "references").glob("*.md")]
    return "\n".join(path.read_text(encoding="utf-8") for path in paths)


def _assert_skill_structure(
    root: Path,
    name: str,
    description_prefix: str,
    references: set[str],
) -> None:
    skill = root / "SKILL.md"
    frontmatter = _frontmatter(skill)
    keys = [line.split(":", 1)[0] for line in frontmatter if ":" in line]

    assert keys == ["name", "description"]
    assert f"name: {name}" in frontmatter
    assert any(line.startswith(description_prefix) for line in frontmatter)
    assert len(skill.read_text(encoding="utf-8").splitlines()) < 500
    assert (root / "agents" / "openai.yaml").is_file()
    assert {path.name for path in (root / "references").glob("*.md")} == references

    routed = set(re.findall(r"`(references/[^`]+\.md)`", skill.read_text()))
    assert routed == {f"references/{reference}" for reference in references}


def test_retrieval_design_skill_structure_and_metadata() -> None:
    _assert_skill_structure(
        DESIGN_ROOT,
        "polygres-retrieval-design",
        "description: Design and review Polygres retrieval",
        {
            "graph-modeling.md",
            "hybrid-and-rag-plan.md",
            "context-design.md",
            "plan-template.md",
            "strategy-selection.md",
            "vector-and-text-design.md",
        },
    )


def test_troubleshooting_skill_structure_and_metadata() -> None:
    _assert_skill_structure(
        TROUBLESHOOTING_ROOT,
        "polygres-troubleshooting",
        "description: Diagnose Polygres",
        {
            "context-and-connectivity.md",
            "context.md",
            "errors-and-escalation.md",
            "jobs-and-migrations.md",
            "projects-and-database.md",
            "retrieval.md",
        },
    )


def test_retrieval_design_is_advisory_and_routes_execution() -> None:
    text = _all_skill_text(DESIGN_ROOT)

    assert "must not mutate" in text.lower()
    assert "$polygres-cli" in text
    assert "$polygres-sdk" in text
    assert "reviewable plan" in text.lower()
    assert "explicit approval" in text.lower()
    assert "unresolved" in text.lower()
    for mutating_command in (
        "polygres graph config apply",
        "polygres graph build",
        "polygres vector configs create",
        "polygres text configs create",
        "polygres migrations apply",
    ):
        assert mutating_command not in text


def test_retrieval_design_covers_strategy_and_bad_input_paths() -> None:
    text = _all_skill_text(DESIGN_ROOT)
    required = (
        "relational",
        "graph",
        "vector",
        "TSVector",
        "fuzzy",
        "hybrid",
        "pgContext",
        "stable row ID",
        "direction",
        "bounded depth",
        "fan-out",
        "embedding model",
        "dimensions",
        "provenance",
        "deduplication",
        "token budget",
        "authorization",
        "readiness",
        "rebuild",
        "reindex",
    )
    for value in required:
        assert value in text

    for unsafe_assumption in (
        "invented row IDs",
        "fuzzy-match schema",
        "dimension mismatch",
        "missing columns",
        "empty sample",
        "unsupported strategy",
    ):
        assert unsafe_assumption in text


def test_retrieval_design_prefers_context_for_new_semantic_retrieval() -> None:
    text = _all_skill_text(DESIGN_ROOT)

    assert "default design surface for new semantic" in text
    assert "Semantic similarity for new setup | pgContext dense retrieval" in text
    assert "already registered configuration" in text


def test_retrieval_plan_has_a_complete_review_contract() -> None:
    template = (DESIGN_ROOT / "references" / "plan-template.md").read_text()
    for heading in (
        "## Outcome",
        "## Known facts",
        "## Unresolved assumptions",
        "## Strategy decision",
        "## Data model",
        "## Configuration plan",
        "## Application plan",
        "## Validation plan",
        "## Risks and approvals",
        "## Handoff",
    ):
        assert heading in template


def test_troubleshooting_uses_only_public_evidence_and_read_only_checks() -> None:
    text = _all_skill_text(TROUBLESHOOTING_ROOT)

    assert "read-only checks first" in text.lower()
    assert "do not mutate while diagnosing" in text.lower()
    assert "$polygres-cli" in text
    assert "$polygres-sdk" in text
    assert "installed `polygres --help`" in text
    assert "private endpoint" in text or "private route" in text
    for forbidden in ("kubectl", "terraform", "az monitor", "GET /", "POST /"):
        assert forbidden not in text


def test_troubleshooting_covers_public_diagnostic_surface() -> None:
    text = _all_skill_text(TROUBLESHOOTING_ROOT)
    commands = (
        "polygres --json whoami",
        "polygres --json projects list",
        "projects status",
        "db info",
        "import status",
        "migrations list",
        "graph status",
        "vector configs list",
        "text configs list",
        "polygres --json --project <project> ready",
        "context capabilities",
        "context collections status",
        "context collections verify",
        "context collections diagnostics",
        "context points status",
        "context operations get",
        "polygres config path",
    )
    for command in commands:
        assert command in text

    for value in (
        "project.readiness()",
        "PolygresValidationError",
        "PolygresAuthError",
        "PolygresPermissionError",
        "PolygresNotFoundError",
        "PolygresRateLimitError",
        "PolygresRuntimeError",
    ):
        assert value in text


def test_troubleshooting_covers_failures_secrets_and_partial_state() -> None:
    text = _all_skill_text(TROUBLESHOOTING_ROOT)

    for value in (
        "authentication",
        "ambiguous project",
        "provisioning",
        "read_only",
        "memory",
        "database",
        "pooler",
        "Runtime API",
        "import job",
        "migration",
        "graph build",
        "vector reindex",
        "text configs reindex",
        "dimension mismatch",
        "empty embedding",
        "fuzzy",
        "rate limit",
        "timeout",
        "partial failure",
        "point reconciliation",
        "idempotency conflict",
        "recall unavailable",
        "request_id",
        "job ID",
        "cursor",
    ):
        assert value in text

    assert "status before retry" in text.lower()
    assert "never log" in text.lower()
    assert "database password" in text
    assert "API key" in text
    assert "POLYGRES_ACCESS_TOKEN" not in text
    assert "PGPASSWORD" not in text


def test_troubleshooting_rules_out_test_fixture_rls_before_pggraph() -> None:
    retrieval = (TROUBLESHOOTING_ROOT / "references" / "retrieval.md").read_text()

    assert "relrowsecurity" in retrieval
    assert "relforcerowsecurity" in retrieval
    assert "fixture/setup incompatibility rather than a\npgGraph defect" in retrieval
    assert "pre-existing user table\nwithout explicit approval" in retrieval


def test_text_search_guidance_matches_one_call_setup_and_maintenance() -> None:
    cli_root = SKILLS_ROOT / "polygres-cli"
    cli_skill = (cli_root / "SKILL.md").read_text()
    cli_retrieval = (cli_root / "references" / "retrieval.md").read_text()
    troubleshooting = (TROUBLESHOOTING_ROOT / "references" / "retrieval.md").read_text()
    design = (DESIGN_ROOT / "references" / "vector-and-text-design.md").read_text()

    for command in (
        "text configs get",
        "text configs update",
        "text configs diagnostics",
        "text configs reindex",
    ):
        assert command in cli_retrieval

    assert "does not create or apply a migration" in " ".join(cli_retrieval.split())
    assert "stored generated" in cli_retrieval
    assert "compound" in cli_retrieval
    assert "default limit" in cli_retrieval
    assert "does not drop a generated" in cli_retrieval
    assert "reindexing a text configuration" in cli_skill
    assert "TEXT_GENERATION_CLEANUP_FAILED" in troubleshooting
    assert "index_found" in troubleshooting and "index_valid" in troubleshooting
    assert "null filter intentionally matches SQL `NULL`" in " ".join(troubleshooting.split())
    assert "one or more text source columns" in design
    assert "does not require a separate migration" in " ".join(design.split())


def test_troubleshooting_verifies_cli_and_sdk_versions_and_origins() -> None:
    context = (TROUBLESHOOTING_ROOT / "references" / "context-and-connectivity.md").read_text()

    assert "polygres --version" in context
    assert 'version("polygres-cli")' in context
    assert 'version("polygres-sdk")' in context
    assert "reinstalled from that checkout" in context
    assert "confirm their import origins" in context
    assert "stale PyPI packages" in context


def test_troubleshooting_report_has_required_evidence_fields() -> None:
    skill = (TROUBLESHOOTING_ROOT / "SKILL.md").read_text()
    for field in (
        "Resolved identity",
        "Resolved project",
        "Symptom",
        "Observed evidence",
        "Likely cause",
        "Safe checks performed",
        "Corrective action",
        "Approval or escalation",
        "IDs retained",
        "Unknowns",
    ):
        assert field in skill


def test_plugin_and_docs_present_all_four_skills() -> None:
    codex = json.loads((PLUGIN_ROOT / ".codex-plugin" / "plugin.json").read_text())
    claude = json.loads((PLUGIN_ROOT / ".claude-plugin" / "plugin.json").read_text())
    package_readme = (PACKAGE_ROOT / "README.md").read_text()
    docs = (
        PACKAGE_ROOT.parents[1] / "apps" / "polygres_docs" / "src" / "content" / "agent-skills.mdx"
    ).read_text()

    assert codex["version"] == PACKAGE_VERSION
    assert claude["version"] == PACKAGE_VERSION
    prompts = "\n".join(codex["interface"]["defaultPrompt"])
    assert "design" in prompts.lower()
    assert "diagnos" in prompts.lower()
    assert "pgcontext" in prompts.lower()
    for name in (
        "polygres-cli",
        "polygres-sdk",
        "polygres-retrieval-design",
        "polygres-troubleshooting",
    ):
        assert name in package_readme
        assert name in docs


def test_gated_skills_are_not_packaged() -> None:
    packaged = {path.name for path in SKILLS_ROOT.iterdir() if path.is_dir()}

    assert "polygres-database-workflows" not in packaged
    assert "polygres-organizations" not in packaged
