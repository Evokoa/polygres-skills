from __future__ import annotations

import ast
import inspect
import json
import re
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest

pytestmark = pytest.mark.heavy

PACKAGE_ROOT = Path(__file__).parents[2]
SDK_ROOT = PACKAGE_ROOT.parents[1] / "packages" / "python-sdk"
SDK_SKILL_ROOT = PACKAGE_ROOT / "plugins" / "polygres" / "skills" / "polygres-sdk"


def _examples() -> list[tuple[Path, str]]:
    return [
        (path, block)
        for path in sorted((SDK_SKILL_ROOT / "references").glob("*.md"))
        if path.name != "mcp-tool-contract.md"
        for block in re.findall(r"```python\n(.*?)```", path.read_text(), flags=re.DOTALL)
    ]


def _text_examples() -> list[tuple[Path, str]]:
    return [
        (path, block)
        for path, block in _examples()
        if any(
            isinstance(node, ast.Call)
            and ast.unparse(node.func).startswith(
                ("project.context.", "project.vector.", "project.hybrid.")
            )
            and any(keyword.arg in {"text", "query"} for keyword in node.keywords)
            for node in ast.walk(ast.parse(block))
        )
    ]


@pytest.fixture
def sdk_client(monkeypatch: pytest.MonkeyPatch) -> Iterator[Callable[..., Any]]:
    if not (SDK_ROOT / "src").is_dir():
        pytest.skip("Python SDK source is not available")
    monkeypatch.syspath_prepend(str(SDK_ROOT / "src"))
    import httpx
    import polygres.client as client_module

    monkeypatch.setattr(client_module, "check_central_version_notices", lambda **kwargs: None)
    clients = []

    def create(handler: Callable[..., Any], *, retries: int = 0) -> Any:
        client = client_module.Polygres(
            api_key=f"poly_live_{uuid4().hex}",
            runtime_url="https://runtime.example.test/v1",
            max_retries=retries,
        )
        client._client.close()
        client._client = httpx.Client(transport=httpx.MockTransport(handler))
        clients.append(client)
        return client

    yield create
    for client in clients:
        client.close()


def _capabilities(*, text: bool = True) -> dict[str, Any]:
    fixtures = json.loads(
        (SDK_ROOT / "tests" / "fixtures" / "context" / "contract-fixtures.json").read_text()
    )
    result = fixtures["responses"]["CapabilitiesResponse"]
    for name in ("dense_search", "text_hybrid", "graph_first", "joint"):
        result.update({name: True, f"{name}_blocker": None, f"{name}_blocker_message": None})
    for name in result:
        if name.startswith("max_"):
            result[name] = 4096
    result["query_embedding_generation"] = text
    return result


def _environment(client: Any) -> dict[str, Any]:
    return {
        "project": client.project(),
        "authorized_tenant_id": "tenant-test",
        "tenant_id": "tenant-test",
        "query_request_id": uuid4().hex,
        "start": {"schema": "public", "table": "documents", "id": "doc-1"},
    }


@pytest.mark.parametrize(("path", "example"), _text_examples())
def test_documented_text_queries_execute_through_existing_methods(
    sdk_client: Callable[..., Any], path: Path, example: str
) -> None:
    import httpx

    fixtures = json.loads(
        (SDK_ROOT / "tests" / "fixtures" / "context" / "contract-fixtures.json").read_text()
    )["responses"]
    requests = []
    response_names = {
        "/v1/context/search": "RankedResponse",
        "/v1/context/hybrid/text": "RankedResponse",
        "/v1/context/hybrid/joint": "ContextJointResponse",
        "/v1/context/query/execute": "QueryExecutionResponse",
    }

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.method == "GET":
            assert request.url.path == "/v1/context/capabilities"
            return httpx.Response(200, json=_capabilities())
        if request.url.path in response_names:
            return httpx.Response(200, json=fixtures[response_names[request.url.path]])
        assert request.url.path in {"/v1/vector/search", "/v1/hybrid/graph-first"}
        return httpx.Response(200, json={"results": [], "has_more": False})

    environment = _environment(sdk_client(handler))
    for statement in ast.parse(example).body:
        exec(compile(ast.Module(body=[statement], type_ignores=[]), str(path), "exec"), environment)
        if isinstance(statement, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "plan" for target in statement.targets
        ):
            assert requests == [], "Constructing a nearest plan must remain local"

    posted = [request for request in requests if request.method == "POST"]
    assert len(posted) == 1
    body = json.loads(posted[0].content)
    assert body.get("embedding") is None
    assert body["use_credits"] is False
    assert "model_id" not in body
    assert "embedding_configuration_id" not in body
    assert posted[0].headers["Idempotency-Key"] == environment["query_request_id"]
    if "/context/" in posted[0].url.path:
        expected_type = response_names[posted[0].url.path]
        assert type(environment["response"]).__name__ == expected_type
    if posted[0].url.path.endswith("/hybrid/text"):
        assert body["text"] == body["query"]
    elif posted[0].url.path.endswith("/hybrid/joint"):
        assert body["text"] != body["query"]
        assert body["weights"]["lexical"] > 0
    elif "plan" in body:
        assert body["plan"]["text"]
        assert "vector" not in body["plan"]
    else:
        assert body["text"]


def test_vector_calls_keep_the_old_runtime_payload_and_text_requires_capability(
    sdk_client: Callable[..., Any],
) -> None:
    import httpx
    from polygres import PolygresValidationError

    requests = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.method == "GET":
            return httpx.Response(200, json=_capabilities(text=False))
        return httpx.Response(200, json={"results": [], "has_more": False})

    project = sdk_client(handler).project()
    project.vector.search([0.1, 0.2], config="documents_embedding")
    assert len(requests) == 1
    body = json.loads(requests[0].content)
    assert body["embedding"] == [0.1, 0.2]
    assert "text" not in body and "use_credits" not in body
    assert "Idempotency-Key" not in requests[0].headers

    with pytest.raises(PolygresValidationError) as failure:
        project.vector.search(text="replication", config="documents_embedding")
    assert failure.value.code == "CONTEXT_CAPABILITY_UNAVAILABLE"
    assert len([request for request in requests if request.method == "POST"]) == 1


def test_python_examples_bind_to_public_sdk_signatures(sdk_client: Callable[..., Any]) -> None:
    import httpx

    project = sdk_client(lambda request: httpx.Response(500)).project()
    namespaces = {name: getattr(project, name) for name in ("context", "vector", "hybrid")}
    checked = 0
    for path, example in _examples():
        for node in ast.walk(ast.parse(example)):
            if not isinstance(node, ast.Call) or any(item.arg is None for item in node.keywords):
                continue
            parts = ast.unparse(node.func).split(".")
            if len(parts) != 3 or parts[0] != "project" or parts[1] not in namespaces:
                continue
            method = getattr(namespaces[parts[1]], parts[2])
            try:
                inspect.signature(method).bind(
                    *node.args, **{keyword.arg: keyword.value for keyword in node.keywords}
                )
            except TypeError as error:
                pytest.fail(f"Invalid SDK call in {path}: {ast.unparse(node)}: {error}")
            checked += 1
    assert checked >= 20
