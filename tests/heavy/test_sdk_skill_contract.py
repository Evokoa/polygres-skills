from __future__ import annotations

import ast
import importlib.util
import inspect
import re
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.heavy

PACKAGE_ROOT = Path(__file__).parents[2]
MONOREPO_ROOT = PACKAGE_ROOT.parents[1]
SDK_SOURCE = MONOREPO_ROOT / "packages" / "python-sdk" / "src"
SDK_SKILL_ROOT = PACKAGE_ROOT / "plugins" / "polygres" / "skills" / "polygres-sdk"


@pytest.mark.skipif(not SDK_SOURCE.is_dir(), reason="Python SDK source is not available")
def test_documented_sdk_methods_exist_with_the_expected_parameters() -> None:
    sys.path.insert(0, str(SDK_SOURCE))
    try:
        from polygres.client import (
            GraphNamespace,
            HybridNamespace,
            Project,
            TextNamespace,
            VectorNamespace,
        )
    finally:
        sys.path.pop(0)

    expected = {
        Project: {"readiness": set(), "connection_info": set()},
        GraphNamespace: {
            "expand": {
                "start",
                "max_depth",
                "relationship_types",
                "direction",
                "filters",
                "limit",
                "cursor",
            },
            "neighborhood": {
                "start",
                "radius",
                "relationship_types",
                "direction",
                "filters",
                "limit",
                "cursor",
            },
            "related": {"start", "relationship_types", "direction", "filters", "limit", "cursor"},
            "path": {"source", "target", "max_depth", "relationship_types", "direction"},
            "connection": {"entities", "max_depth", "relationship_types", "direction"},
        },
        VectorNamespace: {
            "search": {
                "embedding",
                "config",
                "filters",
                "limit",
                "cursor",
                "max_distance",
                "min_similarity",
            },
            "similar_to": {
                "row_id",
                "config",
                "filters",
                "limit",
                "cursor",
                "max_distance",
                "min_similarity",
            },
        },
        TextNamespace: {
            "tsvector": {"query", "config", "filters", "limit", "cursor"},
            "fuzzy": {"query", "config", "filters", "limit", "cursor"},
        },
        HybridNamespace: {
            "graph_first": {
                "start",
                "embedding",
                "config",
                "max_depth",
                "relationship_types",
                "direction",
                "filters",
                "limit",
                "cursor",
            },
            "vector_first": {
                "embedding",
                "config",
                "max_depth",
                "relationship_types",
                "direction",
                "filters",
                "limit",
                "cursor",
            },
            "joint": {
                "start",
                "embedding",
                "config",
                "max_depth",
                "relationship_types",
                "direction",
                "filters",
                "limit",
                "cursor",
            },
        },
    }

    for namespace, methods in expected.items():
        for method_name, parameters in methods.items():
            signature = inspect.signature(getattr(namespace, method_name))
            assert parameters <= set(signature.parameters), (namespace, method_name)


def test_every_python_example_is_syntactically_valid() -> None:
    markdown = [SDK_SKILL_ROOT / "SKILL.md", *(SDK_SKILL_ROOT / "references").glob("*.md")]
    examples: list[tuple[Path, str]] = []
    for path in markdown:
        for block in re.findall(r"```python\n(.*?)```", path.read_text(), flags=re.DOTALL):
            examples.append((path, block))

    assert len(examples) >= 10
    for path, example in examples:
        try:
            ast.parse(example)
        except SyntaxError as error:
            pytest.fail(f"invalid Python example in {path}: {error}")


@pytest.mark.skipif(not SDK_SOURCE.is_dir(), reason="Python SDK source is not available")
def test_documented_exception_names_are_exported_by_the_sdk() -> None:
    init_path = SDK_SOURCE / "polygres" / "__init__.py"
    spec = importlib.util.spec_from_file_location("polygres_public", init_path)
    assert spec and spec.loader
    source = init_path.read_text()
    tree = ast.parse(source)
    exported = next(
        node for node in tree.body if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "__all__" for target in node.targets
        )
    )
    names = {element.value for element in exported.value.elts}  # type: ignore[union-attr]

    assert {
        "PolygresValidationError",
        "PolygresAuthError",
        "PolygresPermissionError",
        "PolygresNotFoundError",
        "PolygresRateLimitError",
        "PolygresRuntimeError",
    } <= names
