from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

PACKAGE_ROOT = Path(__file__).parents[1]
PLUGIN_ROOT = PACKAGE_ROOT / "plugins" / "polygres"
SDK_SKILL_ROOT = PLUGIN_ROOT / "skills" / "polygres-sdk"
VALIDATOR = PACKAGE_ROOT / "scripts" / "validate_package.py"
EXPORTER = PACKAGE_ROOT / "scripts" / "export_public.py"


def _run(script: Path, *arguments: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *(str(argument) for argument in arguments)],
        check=False,
        capture_output=True,
        text=True,
    )


def _copy_package(tmp_path: Path) -> Path:
    destination = tmp_path / "agent-skills"
    shutil.copytree(
        PACKAGE_ROOT,
        destination,
        ignore=shutil.ignore_patterns(".pytest_cache", ".ruff_cache", "__pycache__"),
    )
    return destination


def _frontmatter(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "---"
    return lines[1 : lines.index("---", 1)]


def test_sdk_skill_has_required_structure_and_metadata() -> None:
    skill = SDK_SKILL_ROOT / "SKILL.md"
    frontmatter = _frontmatter(skill)
    keys = [line.split(":", 1)[0] for line in frontmatter if ":" in line]

    assert keys == ["name", "description"]
    assert "name: polygres-sdk" in frontmatter
    assert any(line.startswith("description: Use the Polygres Python SDK") for line in frontmatter)
    assert len(skill.read_text(encoding="utf-8").splitlines()) < 500
    assert (SDK_SKILL_ROOT / "agents" / "openai.yaml").is_file()
    assert {path.name for path in (SDK_SKILL_ROOT / "references").glob("*.md")} == {
        "client-setup.md",
        "errors-pagination-testing.md",
        "graph-retrieval.md",
        "hybrid-and-rag.md",
        "vector-and-text.md",
    }


def test_sdk_skill_routes_every_reference_and_avoids_deep_links() -> None:
    skill_text = (SDK_SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    references = set(re.findall(r"`(references/[^`]+\.md)`", skill_text))

    assert references == {
        "references/client-setup.md",
        "references/errors-pagination-testing.md",
        "references/graph-retrieval.md",
        "references/hybrid-and-rag.md",
        "references/vector-and-text.md",
    }
    assert "../" not in skill_text
    for reference in references:
        assert (SDK_SKILL_ROOT / reference).is_file()


def test_sdk_skill_covers_the_complete_priority_one_surface() -> None:
    all_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [SDK_SKILL_ROOT / "SKILL.md", *(SDK_SKILL_ROOT / "references").glob("*.md")]
    )
    required_calls = {
        "project.readiness()",
        "project.connection_info()",
        "project.graph.expand(",
        "project.graph.neighborhood(",
        "project.graph.related(",
        "project.graph.path(",
        "project.graph.connection(",
        "project.vector.search(",
        "project.vector.similar_to(",
        "project.text.tsvector(",
        "project.text.fuzzy(",
        "project.hybrid.graph_first(",
        "project.hybrid.vector_first(",
        "project.hybrid.joint(",
        ".auto_paging_iter()",
    }

    assert required_calls <= {call for call in required_calls if call in all_text}
    for concept in (
        "PolygresValidationError",
        "PolygresAuthError",
        "PolygresPermissionError",
        "PolygresNotFoundError",
        "PolygresRateLimitError",
        "PolygresRuntimeError",
        "row ID",
        "provenance",
        "deduplication",
        "token budget",
    ):
        assert concept in all_text


def test_sdk_skill_preserves_endpoint_and_secret_boundaries() -> None:
    all_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [SDK_SKILL_ROOT / "SKILL.md", *(SDK_SKILL_ROOT / "references").glob("*.md")]
    )

    assert "POLYGRES_API_KEY" in all_text
    assert "POLYGRES_RUNTIME_URL" in all_text
    assert "control-plane" in all_text
    assert "passwordless" in all_text
    assert "Never log" in all_text or "never log" in all_text
    assert "private endpoint" in all_text or "private route" in all_text
    assert "access token" not in all_text.lower()
    assert not re.search(r"(?:sk|pgs|token)[_-][A-Za-z0-9]{20,}", all_text)


def test_sdk_references_cover_invalid_ambiguous_and_fuzzy_inputs() -> None:
    graph = (SDK_SKILL_ROOT / "references" / "graph-retrieval.md").read_text()
    vector_text = (SDK_SKILL_ROOT / "references" / "vector-and-text.md").read_text()
    errors = (SDK_SKILL_ROOT / "references" / "errors-pagination-testing.md").read_text()

    assert "invent" in graph.lower() and "row ID" in graph
    assert "max_depth" in graph and "direction" in graph and "fan-out" in graph
    assert "dimension" in vector_text and "NaN" in vector_text
    assert "empty" in vector_text.lower() and "fuzzy" in vector_text.lower()
    assert "timeout" in errors.lower() and "request_id" in errors
    assert "malformed" in errors.lower() and "mock" in errors.lower()


def test_plugin_metadata_exposes_distinct_cli_and_sdk_prompts() -> None:
    codex = json.loads((PLUGIN_ROOT / ".codex-plugin" / "plugin.json").read_text())
    claude = json.loads((PLUGIN_ROOT / ".claude-plugin" / "plugin.json").read_text())
    prompts = codex["interface"]["defaultPrompt"]

    assert any("CLI" in prompt or "import" in prompt.lower() for prompt in prompts)
    assert any("SDK" in prompt or "application" in prompt.lower() for prompt in prompts)
    assert all(len(prompt) <= 128 for prompt in prompts)
    assert "SDK" in codex["description"] or "application" in codex["description"]
    assert "SDK" in claude["description"] or "application" in claude["description"]


def test_validator_accepts_the_canonical_package() -> None:
    result = _run(VALIDATOR, PACKAGE_ROOT)

    assert result.returncode == 0, result.stderr
    assert result.stdout == "Validated 4 skills in the Polygres plugin.\n"
    assert result.stderr == ""


@pytest.mark.parametrize(
    ("mutation", "expected_error"),
    [
        ("missing-description", "frontmatter must contain only name and description"),
        ("directory-mismatch", "directory must match frontmatter name"),
        ("broken-reference", "reference does not exist"),
        ("reference-traversal", "reference escapes the skill directory"),
        ("placeholder", "contains forbidden placeholder TODO"),
        ("fuzzy-trigger", "skill descriptions are too similar"),
    ],
)
def test_validator_rejects_malformed_and_ambiguous_packages(
    tmp_path: Path, mutation: str, expected_error: str
) -> None:
    package = _copy_package(tmp_path)
    sdk = package / "plugins" / "polygres" / "skills" / "polygres-sdk"
    skill = sdk / "SKILL.md"

    if mutation == "missing-description":
        skill.write_text(skill.read_text().replace("description:", "summary:", 1))
    elif mutation == "directory-mismatch":
        skill.write_text(skill.read_text().replace("name: polygres-sdk", "name: polygres-skd"))
    elif mutation == "broken-reference":
        skill.write_text(skill.read_text().replace("client-setup.md", "missing.md", 1))
    elif mutation == "reference-traversal":
        skill.write_text(
            skill.read_text().replace("references/client-setup.md", "references/../../README.md", 1)
        )
    elif mutation == "placeholder":
        skill.write_text(f"{skill.read_text()}\nTODO: fill this in\n")
    elif mutation == "fuzzy-trigger":
        cli = package / "plugins" / "polygres" / "skills" / "polygres-cli" / "SKILL.md"
        cli_description = next(
            line for line in _frontmatter(cli) if line.startswith("description:")
        )
        lines = skill.read_text().splitlines()
        lines[2] = cli_description.replace("CLI", "CLl")
        skill.write_text("\n".join(lines) + "\n")

    result = _run(package / "scripts" / "validate_package.py", package)

    assert result.returncode == 1
    assert expected_error in result.stderr
    assert result.stdout == ""


def test_exporter_creates_a_deterministic_mirror_for_every_skill(tmp_path: Path) -> None:
    destination = tmp_path / "export"

    first = _run(EXPORTER, PACKAGE_ROOT, destination)
    assert first.returncode == 0, first.stderr
    assert first.stdout == "Exported 4 skills.\n"
    for name in (
        "polygres-cli",
        "polygres-retrieval-design",
        "polygres-sdk",
        "polygres-troubleshooting",
    ):
        source_skill = PLUGIN_ROOT / "skills" / name / "SKILL.md"
        exported_skill = destination / "skills" / name / "SKILL.md"
        assert exported_skill.read_bytes() == source_skill.read_bytes()

    (destination / "stale.txt").write_text("stale")
    second = _run(EXPORTER, PACKAGE_ROOT, destination)
    assert second.returncode == 0, second.stderr
    assert not (destination / "stale.txt").exists()


def test_exporter_rejects_a_destination_inside_the_source(tmp_path: Path) -> None:
    result = _run(EXPORTER, PACKAGE_ROOT, PACKAGE_ROOT / "nested-export")

    assert result.returncode == 2
    assert "destination must be outside the source package" in result.stderr
