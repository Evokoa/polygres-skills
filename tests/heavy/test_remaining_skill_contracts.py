from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.heavy

PACKAGE_ROOT = Path(__file__).parents[2]
MONOREPO_ROOT = PACKAGE_ROOT.parents[1]
CLI_SOURCE = MONOREPO_ROOT / "packages" / "python-cli" / "src"
SDK_SOURCE = MONOREPO_ROOT / "packages" / "python-sdk" / "src"


def _top_level_commands(parser: argparse.ArgumentParser) -> set[str]:
    action = next(item for item in parser._actions if isinstance(item, argparse._SubParsersAction))
    return set(action.choices)


@pytest.mark.skipif(not CLI_SOURCE.is_dir(), reason="Python CLI source is not available")
def test_troubleshooting_commands_parse_with_the_public_cli() -> None:
    sys.path.insert(0, str(CLI_SOURCE))
    try:
        from polygres_cli.cli import build_parser
    finally:
        sys.path.pop(0)

    parser = build_parser()
    project_id = "p0123456789abcdef0123456"
    job_id = "00000000-0000-0000-0000-000000000000"
    samples = [
        ["--json", "whoami"],
        ["--json", "projects", "list"],
        ["--json", "--project", project_id, "projects", "status"],
        ["--json", "--project", project_id, "db", "info"],
        ["--json", "--project", project_id, "import", "status", job_id],
        ["--json", "--project", project_id, "migrations", "list"],
        ["--json", "--project", project_id, "graph", "status"],
        ["--json", "--project", project_id, "vector", "configs", "list"],
        ["--json", "--project", project_id, "text", "configs", "list"],
        ["--json", "--project", project_id, "ready"],
        ["config", "path"],
    ]

    for sample in samples:
        parsed = parser.parse_args(sample)
        assert hasattr(parsed, "func"), sample


@pytest.mark.skipif(not CLI_SOURCE.is_dir(), reason="Python CLI source is not available")
def test_gated_cli_surfaces_are_still_absent() -> None:
    sys.path.insert(0, str(CLI_SOURCE))
    try:
        from polygres_cli.cli import build_parser
    finally:
        sys.path.pop(0)

    commands = _top_level_commands(build_parser())

    assert "skills" not in commands
    assert "sql" not in commands
    assert "query" not in commands
    assert "dump" not in commands


@pytest.mark.skipif(not SDK_SOURCE.is_dir(), reason="Python SDK source is not available")
def test_troubleshooting_sdk_symbols_match_the_public_sdk() -> None:
    sys.path.insert(0, str(SDK_SOURCE))
    try:
        import polygres
        from polygres.client import Project
    finally:
        sys.path.pop(0)

    assert callable(Project.readiness)
    for name in (
        "PolygresValidationError",
        "PolygresAuthError",
        "PolygresPermissionError",
        "PolygresNotFoundError",
        "PolygresRateLimitError",
        "PolygresRuntimeError",
    ):
        assert name in polygres.__all__
