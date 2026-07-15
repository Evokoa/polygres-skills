from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

PACKAGE_ROOT = Path(__file__).parents[1]
PLUGIN_ROOT = PACKAGE_ROOT / "plugins" / "polygres"
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
    assert manifest["version"] == "0.2.0"
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
    assert manifest["version"] == "0.2.0"
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


@pytest.mark.skipif(not CLI_ENTRYPOINT.is_file(), reason="CLI source is not part of this checkout")
def test_documented_command_shapes_parse_with_current_cli() -> None:
    sys.path.insert(0, str(CLI_SOURCE))
    try:
        from polygres_cli.cli import build_parser
    finally:
        sys.path.pop(0)

    parser = build_parser()
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
        ["ready"],
        ["config", "path"],
    ]
    for sample in samples:
        parsed = parser.parse_args(sample)
        assert hasattr(parsed, "func"), sample
