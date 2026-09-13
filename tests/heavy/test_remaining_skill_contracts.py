from __future__ import annotations

import argparse
import json
import re
import shlex
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

pytestmark = pytest.mark.heavy

PACKAGE_ROOT = Path(__file__).parents[2]
MONOREPO_ROOT = PACKAGE_ROOT.parents[1]
CLI_SOURCE = MONOREPO_ROOT / "packages" / "python-cli" / "src"
SDK_SOURCE = MONOREPO_ROOT / "packages" / "python-sdk" / "src"
MCP_SOURCE = MONOREPO_ROOT / "services" / "mcp"
LIB_SOURCE = MONOREPO_ROOT / "packages" / "polygres-lib" / "python" / "src"
EMBEDDING_REFERENCE = (
    PACKAGE_ROOT
    / "plugins"
    / "polygres"
    / "skills"
    / "polygres-troubleshooting"
    / "references"
    / "embeddings.md"
)


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
        ["--json", "--project", project_id, "text", "configs", "get", "documents"],
        [
            "--json",
            "--project",
            project_id,
            "text",
            "configs",
            "diagnostics",
            "documents",
        ],
        ["--json", "--project", project_id, "context", "capabilities"],
        [
            "--json",
            "--project",
            project_id,
            "context",
            "collections",
            "status",
            job_id,
        ],
        ["--json", "--project", project_id, "context", "collections", "verify", job_id],
        ["--json", "--project", project_id, "context", "collections", "diagnostics", job_id],
        ["--json", "--project", project_id, "context", "points", "status", job_id],
        ["--json", "--project", project_id, "context", "operations", "get", job_id],
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


@pytest.mark.skipif(not CLI_SOURCE.is_dir(), reason="Python CLI source is not available")
def test_embedding_diagnostic_commands_only_read_public_runtime_state(monkeypatch) -> None:
    monkeypatch.syspath_prepend(str(CLI_SOURCE))
    from polygres_cli.cli import build_parser

    parser = build_parser()
    project_id = "p0123456789abcdef0123456"
    configuration_id = "00000000-0000-4000-8000-000000000001"
    runtime = Mock()
    runtime.request.return_value = {}
    blocks = re.findall(
        r"```console\n(.*?)\n```", EMBEDDING_REFERENCE.read_text(), flags=re.DOTALL
    )
    parsed_commands = []
    for block in blocks:
        for line in block.splitlines():
            command = line.replace("<project>", project_id).replace(
                "<configuration-uuid>", configuration_id
            )
            if not command.startswith("polygres ") or command.endswith("--help"):
                continue
            args = parser.parse_args(shlex.split(command)[1:])
            if getattr(args, "resource", None) != "embeddings":
                continue
            context = SimpleNamespace(
                args=args, client=SimpleNamespace(_runtime=runtime), json=False, quiet=True
            )
            assert args.func(context, args) == 0
            parsed_commands.append(args.embedding_action)

    assert set(parsed_commands) == {"sources", "models", "usage", "list", "get", "context"}
    for command, call in zip(parsed_commands, runtime.request.call_args_list, strict=True):
        project, scope, method, path = call.args
        assert project == project_id
        assert method == "GET"
        assert path.startswith("/embeddings/")
        assert scope == ("context:manage" if command in {"sources", "context"} else "context:read")
        assert call.kwargs["json"] is None
        assert call.kwargs["headers"] is None
        assert call.kwargs["read_only_retry"] is True


@pytest.mark.skipif(not MCP_SOURCE.is_dir(), reason="MCP source is not available")
def test_embedding_mcp_error_recovery_preserves_retryability_and_request_id(monkeypatch) -> None:
    pytest.importorskip("fastmcp")
    monkeypatch.syspath_prepend(str(MCP_SOURCE))
    monkeypatch.syspath_prepend(str(LIB_SOURCE))
    from polygres_lib.errors import catalog_error
    from polygres_mcp.errors import public_tool_error

    rows = re.findall(
        r"^\| `(\w+)` \| \d+ \| `(\w+)` \|",
        EMBEDDING_REFERENCE.read_text(),
        flags=re.MULTILINE,
    )
    for code, retry_class in rows:
        response = json.loads(
            public_tool_error(catalog_error(code), request_id="req_embedding_diagnostic")
        )
        assert set(response) == {"error", "request_id"}
        assert response["request_id"] == "req_embedding_diagnostic"
        assert response["error"]["code"] == code
        assert response["error"]["message"]
        assert response["error"]["retryable"] is (
            retry_class in {"bounded_retry", "dependency_retry", "after_delay"}
        )
        assert set(response["error"]) <= {"code", "message", "retryable", "variant", "details"}
