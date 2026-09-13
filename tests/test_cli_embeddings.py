from __future__ import annotations

import io
import json
import re
import shlex
from pathlib import Path

import pytest

PACKAGE_ROOT = Path(__file__).parents[1]
CLI_SOURCE = PACKAGE_ROOT.parents[1] / "packages" / "python-cli" / "src"
REFERENCE_ROOT = PACKAGE_ROOT / "plugins" / "polygres" / "skills" / "polygres-cli" / "references"
EXAMPLE_UUID = "00000000-0000-4000-8000-000000000001"

pytestmark = pytest.mark.skipif(
    not CLI_SOURCE.is_dir(), reason="CLI source is not part of this checkout"
)


@pytest.fixture
def cli(monkeypatch):
    monkeypatch.syspath_prepend(str(CLI_SOURCE))
    from polygres_cli import cli

    return cli


def _commands(reference: str) -> list[list[str]]:
    text = (REFERENCE_ROOT / reference).read_text(encoding="utf-8")
    commands = []
    for block in re.findall(r"```bash\n(.*?)\n```", text, flags=re.DOTALL):
        for line in block.replace("\\\n", " ").splitlines():
            if not line.startswith("polygres "):
                continue
            tokens = shlex.split(line)[1:]
            commands.append(
                [
                    EXAMPLE_UUID if token.endswith("-uuid>") else "example-project"
                    if token == "<project>"
                    else token
                    for token in tokens
                ]
            )
    return commands


def _json_examples(reference: str) -> list[dict]:
    text = (REFERENCE_ROOT / reference).read_text(encoding="utf-8")
    return [
        json.loads(block.replace("MODEL_UUID", EXAMPLE_UUID))
        for block in re.findall(r"```json\n(.*?)\n```", text, flags=re.DOTALL)
    ]


@pytest.mark.parametrize("reference", ["embeddings.md", "context.md"])
def test_documented_commands_parse_with_current_cli(cli, reference):
    parser = cli.build_parser()
    commands = _commands(reference)
    assert commands
    for command in commands:
        parser.parse_args(command)


def test_embedding_examples_validate_with_public_request_contracts(cli):
    from polygres_cli._vendor.polygres_lib.embeddings.models import (
        EmbeddingConfigurationCreate,
        EmbeddingConfigurationUpdate,
        EmbeddingRemoveRequest,
    )

    create, update = _json_examples("embeddings.md")
    EmbeddingConfigurationCreate.model_validate(create)
    EmbeddingConfigurationUpdate.model_validate(update)
    for command in _commands("embeddings.md"):
        args = cli.build_parser().parse_args(command)
        if getattr(args, "embedding_action", None) == "remove":
            EmbeddingRemoveRequest.model_validate(
                {
                    "expected_version": args.expected_version,
                    "delete_managed_output": args.delete_output,
                }
            )


def test_text_query_examples_produce_valid_payloads(cli, tmp_path, monkeypatch):
    from polygres_cli._vendor.polygres_lib.context import (
        DenseSearchRequest,
        GroupedSearchRequest,
        JointSearchRequest,
        TextHybridSearchRequest,
    )

    monkeypatch.chdir(tmp_path)
    (tmp_path / "question.txt").write_text("How does replication work?", encoding="utf-8")
    query = _json_examples("context.md")[0]
    (tmp_path / "query.json").write_text(json.dumps(query), encoding="utf-8")
    models = {
        "search": (DenseSearchRequest, "search"),
        "grouped-search": (GroupedSearchRequest, "grouped_search"),
        "text-hybrid": (TextHybridSearchRequest, "text_hybrid"),
        "joint": (JointSearchRequest, "joint"),
    }
    checked = set()
    for command in _commands("context.md") + _commands("embeddings.md"):
        args = cli.build_parser().parse_args(command)
        action = getattr(args, "context_action", None)
        if action not in models:
            continue
        monkeypatch.setattr("sys.stdin", io.StringIO("How does replication work?"))
        model, mode = models[action]
        payload = (
            cli._context_joint_payload(args)
            if mode == "joint"
            else cli._context_ranked_payload(args, model, mode)
        )
        model.model_validate(payload)
        assert payload["text"].strip()
        assert payload["use_credits"] is False
        assert "embedding" not in payload
        assert cli._context_query_options(args, payload)["idempotency_key"]
        if mode == "text_hybrid":
            assert payload["text"] == payload["query"]
        if mode == "joint":
            assert payload["text"] != payload["query"]
        checked.add(action)
    assert checked == set(models)
