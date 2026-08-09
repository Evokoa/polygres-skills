from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

PACKAGE_ROOT = Path(__file__).parents[1]
PLUGIN_ROOT = PACKAGE_ROOT / "plugins" / "polygres"
PACKAGE_VERSION = (PACKAGE_ROOT / "VERSION").read_text().strip()
SKILL_ROOT = PLUGIN_ROOT / "skills" / "polygres-cli"
MONOREPO_ROOT = PACKAGE_ROOT.parents[1]
CLI_SOURCE = MONOREPO_ROOT / "packages" / "python-cli" / "src"
CLI_ENTRYPOINT = CLI_SOURCE / "polygres_cli" / "cli.py"


def test_skill_frontmatter_and_required_resources() -> None:
    skill = SKILL_ROOT / "SKILL.md"
    text = skill.read_text(encoding="utf-8")
    lines = text.splitlines()
    assert lines[0] == "---"
    closing = lines.index("---", 1)
    frontmatter = lines[1:closing]
    keys = [line.split(":", 1)[0] for line in frontmatter if ":" in line]
    assert keys == ["name", "description"]
    assert "name: polygres-cli" in frontmatter
    assert any(line.startswith("description: Use the Polygres CLI") for line in frontmatter)
    assert len(lines) < 500

    expected = {
        "authentication-and-projects.md",
        "automation-and-errors.md",
        "context.md",
        "data-imports.md",
        "database-and-keys.md",
        "migrations.md",
        "retrieval.md",
    }
    assert {path.name for path in (SKILL_ROOT / "references").glob("*.md")} == expected
    assert (SKILL_ROOT / "scripts" / "prepare_import.py").is_file()
    assert (SKILL_ROOT / "agents" / "openai.yaml").is_file()


def test_codex_manifest_and_marketplace_are_consistent() -> None:
    manifest = json.loads((PLUGIN_ROOT / ".codex-plugin" / "plugin.json").read_text())
    marketplace = json.loads(
        (PACKAGE_ROOT / ".agents" / "plugins" / "marketplace.json").read_text()
    )
    entry = marketplace["plugins"][0]

    assert manifest["name"] == "polygres"
    assert manifest["version"] == PACKAGE_VERSION
    assert manifest["skills"] == "./skills/"
    assert (PLUGIN_ROOT / manifest["skills"]).is_dir()
    assert entry["name"] == manifest["name"]
    assert entry["source"] == {"source": "local", "path": "./plugins/polygres"}
    assert (PACKAGE_ROOT / entry["source"]["path"]).resolve() == PLUGIN_ROOT.resolve()
    assert entry["policy"] == {
        "installation": "AVAILABLE",
        "authentication": "ON_USE",
    }
    prompts = manifest["interface"]["defaultPrompt"]
    assert 1 <= len(prompts) <= 3
    assert all(len(prompt) <= 128 for prompt in prompts)


def test_claude_manifest_and_marketplace_are_consistent() -> None:
    manifest = json.loads((PLUGIN_ROOT / ".claude-plugin" / "plugin.json").read_text())
    marketplace = json.loads((PACKAGE_ROOT / ".claude-plugin" / "marketplace.json").read_text())
    entry = marketplace["plugins"][0]

    assert manifest["name"] == "polygres"
    assert manifest["version"] == PACKAGE_VERSION
    assert entry["name"] == manifest["name"]
    assert entry["version"] == manifest["version"]
    assert entry["source"] == "./plugins/polygres"
    assert (PACKAGE_ROOT / entry["source"]).resolve() == PLUGIN_ROOT.resolve()


def test_package_contains_no_placeholders_or_em_dashes() -> None:
    checked_suffixes = {".md", ".json", ".yaml", ".py"}
    for path in PACKAGE_ROOT.rglob("*"):
        if not path.is_file() or path.suffix not in checked_suffixes:
            continue
        if "tests" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        assert "TODO" not in text, path
        assert "FIXME" not in text, path
        assert "[TODO:" not in text, path
        assert "—" not in text, path


def test_reference_links_from_skill_exist() -> None:
    skill_text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    referenced = set(re.findall(r"`(references/[^`]+\.md)`", skill_text))
    assert referenced
    for relative in referenced:
        assert (SKILL_ROOT / relative).is_file(), relative


def test_cli_guidance_routes_new_semantic_setup_to_context() -> None:
    skill_text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    retrieval = (SKILL_ROOT / "references" / "retrieval.md").read_text(encoding="utf-8")

    assert "configure graph, text, or Polygres AI Context retrieval" in skill_text
    assert "For new semantic retrieval" in retrieval
    assert "polygres context collections create" in retrieval
    assert "vector configs create` path is retired" in retrieval


def test_cli_pggraph_fixture_guidance_does_not_manufacture_rls_failures() -> None:
    retrieval = (SKILL_ROOT / "references" / "retrieval.md").read_text(encoding="utf-8")

    assert "do not enable Row\nLevel Security" in retrieval
    assert "relrowsecurity = false" in retrieval
    assert "relforcerowsecurity = false" in retrieval
    assert "not a pgGraph product failure" in retrieval
    assert "pre-existing user table without explicit approval" in retrieval


def test_cli_live_testing_refreshes_cli_and_sdk_from_checkout() -> None:
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")

    assert "`polygres --version`" in skill
    assert "reinstall both `polygres-cli` and `polygres-sdk`" in skill
    assert "verify their versions\n   and import origins" in skill
    assert "Do not substitute PyPI packages" in skill
    assert "current skill compatibility record" in skill


@pytest.mark.skipif(not CLI_ENTRYPOINT.is_file(), reason="CLI source is not part of this checkout")
def test_documented_command_shapes_parse_with_current_cli() -> None:
    sys.path.insert(0, str(CLI_SOURCE))
    try:
        from polygres_cli.cli import build_parser
    finally:
        sys.path.pop(0)

    parser = build_parser()
    context_id = "00000000-0000-0000-0000-000000000000"
    samples = [
        ["login"],
        ["logout"],
        ["whoami"],
        ["projects", "list"],
        ["projects", "use", "example"],
        ["projects", "create", "example", "--no-wait"],
        ["projects", "status"],
        ["env"],
        ["db", "info"],
        ["db", "psql"],
        ["keys", "list"],
        ["keys", "create", "automation"],
        ["keys", "revoke", "00000000-0000-0000-0000-000000000000", "--yes"],
        ["--json", "import", "csv", "data.csv", "--table", "documents", "--wait"],
        ["import", "status", "00000000-0000-0000-0000-000000000000"],
        ["migrations", "list"],
        ["migrations", "apply", "--file", "migration.sql"],
        ["graph", "discover"],
        ["graph", "config", "export"],
        ["graph", "config", "apply", "--file", "graph.json"],
        ["graph", "build"],
        ["graph", "status"],
        ["vector", "configs", "list"],
        [
            "vector",
            "configs",
            "create",
            "documents",
            "--table",
            "documents",
            "--embedding-column",
            "embedding",
            "--dimensions",
            "1536",
        ],
        ["vector", "configs", "delete", "00000000-0000-0000-0000-000000000000", "--yes"],
        ["vector", "reindex", "00000000-0000-0000-0000-000000000000"],
        ["text", "configs", "list"],
        [
            "text",
            "configs",
            "create-fuzzy",
            "body",
            "--table",
            "documents",
            "--text-column",
            "body",
        ],
        [
            "text",
            "configs",
            "create-tsvector",
            "body",
            "--table",
            "documents",
            "--tsvector-column",
            "body_tsv",
        ],
        ["text", "configs", "delete", "00000000-0000-0000-0000-000000000000", "--yes"],
        ["context", "capabilities"],
        ["context", "sources", "discover", "--schema", "public"],
        ["context", "sources", "preflight", "--file", "context.json"],
        ["context", "collections", "list"],
        ["context", "collections", "get", context_id],
        ["context", "collections", "status", context_id],
        ["context", "collections", "verify", context_id],
        ["context", "collections", "diagnostics", context_id],
        [
            "context",
            "collections",
            "create",
            "support_docs",
            "--source",
            "existing",
            "--schema",
            "public",
            "--table",
            "documents",
            "--source-key-column",
            "id",
            "--vector-column",
            "embedding",
            "--dimensions",
            "768",
            "--metric",
            "cosine",
            "--text-column",
            "content",
            "--result-column",
            "title",
            "--filter-column",
            "tenant_id",
            "--no-wait",
            "--idempotency-key",
            context_id,
        ],
        ["context", "collections", "update", context_id, "--max-search-limit", "500"],
        ["context", "collections", "set-default", context_id, "--no-wait"],
        ["context", "collections", "reindex", context_id, "--no-wait"],
        ["context", "collections", "delete", context_id, "--yes", "--no-wait"],
        ["context", "filters", "list", context_id],
        [
            "context",
            "filters",
            "add-column",
            context_id,
            "--key",
            "tenant_id",
            "--column",
            "tenant_id",
            "--no-wait",
        ],
        [
            "context",
            "filters",
            "add-jsonb-path",
            context_id,
            "--key",
            "topic",
            "--column",
            "metadata",
            "--path",
            "topic",
            "--no-wait",
        ],
        ["context", "points", "upsert", context_id, "doc_1", "doc_2"],
        ["context", "points", "delete", context_id, "doc_1"],
        ["context", "points", "status", context_id],
        ["context", "points", "reconcile", context_id, "--no-wait"],
        ["context", "points", "scroll", context_id, "--limit", "50", "--cursor", "opaque"],
        ["context", "operations", "list", "--collection-id", context_id],
        ["context", "operations", "get", context_id],
        ["context", "operations", "wait", context_id, "--timeout", "1800"],
        ["context", "operations", "cancel", context_id, "--no-wait"],
        ["context", "operations", "retry", context_id, "--no-wait"],
        ["context", "count", "support_docs", "--filter-json", "{}"],
        ["context", "facets", "support_docs", "category", "--limit", "10"],
        ["context", "search", "support_docs", "--embedding-file", "embedding.json"],
        [
            "context",
            "text-hybrid",
            "support_docs",
            "--embedding-file",
            "embedding.json",
            "--query",
            "current guidance",
        ],
        [
            "context",
            "graph-first",
            "support_docs",
            "--embedding-file",
            "embedding.json",
            "--start-schema",
            "public",
            "--start-table",
            "accounts",
            "--start-id",
            "acct_123",
        ],
        [
            "context",
            "vector-first",
            "support_docs",
            "--embedding-file",
            "embedding.json",
        ],
        [
            "context",
            "rank-fusion",
            "support_docs",
            "--embedding-file",
            "embedding.json",
            "--start-schema",
            "public",
            "--start-table",
            "accounts",
            "--start-id",
            "acct_123",
        ],
        [
            "context",
            "joint",
            "support_docs",
            "--embedding-file",
            "embedding.json",
            "--query",
            "current guidance",
        ],
        [
            "context",
            "grouped-search",
            "support_docs",
            "--embedding-file",
            "embedding.json",
            "--group-by",
            "tenant_id",
        ],
        [
            "context",
            "recall-check",
            "support_docs",
            "--embedding-file",
            "embedding.json",
            "--minimum-recall",
            "0.95",
        ],
        ["ready"],
        ["config", "path"],
    ]
    for sample in samples:
        parsed = parser.parse_args(sample)
        assert hasattr(parsed, "func"), sample
