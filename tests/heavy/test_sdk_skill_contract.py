from __future__ import annotations

import ast
import importlib.util
import inspect
import re
import sys
from pathlib import Path
from typing import get_args, get_type_hints

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
        from polygres.context import ContextNamespace
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
        ContextNamespace: {
            "get_capabilities": {"timeout"},
            "discover_sources": {"schema_names", "timeout"},
            "preflight": {
                "name",
                "source",
                "vector",
                "text_column",
                "result_columns",
                "filter_columns",
                "jsonb_filter_paths",
                "index_kind",
                "max_search_limit",
                "timeout",
            },
            "list_collections": {"status", "limit", "cursor", "timeout"},
            "get_collection": {"collection_id", "timeout"},
            "get_collection_status": {"collection_id", "timeout"},
            "verify_collection": {"collection_id", "timeout"},
            "get_collection_diagnostics": {"collection_id", "timeout"},
            "create_collection": {
                "name",
                "source",
                "vector",
                "text_column",
                "result_columns",
                "filter_columns",
                "jsonb_filter_paths",
                "index_kind",
                "max_search_limit",
                "idempotency_key",
                "timeout",
            },
            "update_collection": {
                "collection_id",
                "text_column",
                "result_columns",
                "max_search_limit",
                "idempotency_key",
                "timeout",
            },
            "set_default_collection": {"collection_id", "idempotency_key", "timeout"},
            "reindex_collection": {"collection_id", "idempotency_key", "timeout"},
            "delete_collection": {
                "collection_id",
                "confirm_collection_id",
                "idempotency_key",
                "timeout",
            },
            "list_filters": {"collection_id", "timeout"},
            "add_filter_column": {
                "collection_id",
                "key",
                "column",
                "idempotency_key",
                "timeout",
            },
            "add_jsonb_filter_path": {
                "collection_id",
                "key",
                "column",
                "path",
                "idempotency_key",
                "timeout",
            },
            "get_point_status": {"collection_id", "timeout"},
            "scroll_points": {"collection_id", "limit", "cursor", "timeout"},
            "upsert_points": {"collection_id", "source_keys", "idempotency_key", "timeout"},
            "delete_points": {"collection_id", "source_keys", "idempotency_key", "timeout"},
            "reconcile_points": {"collection_id", "idempotency_key", "timeout"},
            "list_operations": {"collection_id", "kind", "status", "limit", "cursor", "timeout"},
            "get_operation": {"operation_id", "timeout"},
            "wait_for_operation": {"operation_or_id", "timeout"},
            "cancel_operation": {"operation_id", "idempotency_key", "timeout"},
            "retry_operation": {"operation_id", "idempotency_key", "timeout"},
            "count": {"collection", "filter", "timeout"},
            "facets": {"collection", "field", "filter", "limit", "timeout"},
            "search": {"collection", "embedding", "filter", "limit", "timeout"},
            "grouped_search": {
                "collection",
                "embedding",
                "group_by",
                "group_limit",
                "limit",
                "timeout",
            },
            "recall_check": {
                "collection",
                "embedding",
                "filter",
                "minimum_recall",
                "limit",
                "timeout",
            },
            "text_hybrid": {"collection", "embedding", "query", "limit", "timeout"},
            "graph_first": {
                "collection",
                "embedding",
                "start",
                "max_depth",
                "graph_limit",
                "relationship_types",
                "direction",
                "filter",
                "limit",
                "timeout",
            },
            "vector_first": {
                "collection",
                "embedding",
                "context_limit",
                "max_depth",
                "graph_limit",
                "relationship_types",
                "direction",
                "filter",
                "limit",
                "timeout",
            },
            "rank_fusion": {
                "collection",
                "embedding",
                "start",
                "context_limit",
                "max_depth",
                "graph_limit",
                "relationship_types",
                "direction",
                "context_weight",
                "graph_weight",
                "filter",
                "limit",
                "timeout",
            },
            "joint": {
                "collection",
                "embedding",
                "query",
                "starts",
                "filter",
                "relationship_types",
                "direction",
                "max_depth",
                "context_limit",
                "seed_limit",
                "graph_limit",
                "traversal_limit",
                "semantic_weight",
                "lexical_weight",
                "graph_weight",
                "limit",
                "timeout",
            },
        },
    }

    for namespace, methods in expected.items():
        for method_name, parameters in methods.items():
            signature = inspect.signature(getattr(namespace, method_name))
            actual = set(signature.parameters) - {"self"}
            if namespace is ContextNamespace:
                assert parameters == actual, (namespace, method_name)
            else:
                assert parameters <= actual, (namespace, method_name)


@pytest.mark.skipif(not SDK_SOURCE.is_dir(), reason="Python SDK source is not available")
def test_context_sdk_defaults_and_return_unions_match_the_skill() -> None:
    sys.path.insert(0, str(SDK_SOURCE))
    try:
        from polygres import ContextOperation, PointMutationResponse, RankedResponse
        from polygres.context import ContextNamespace
    finally:
        sys.path.pop(0)

    create = inspect.signature(ContextNamespace.create_collection)
    assert create.parameters["index_kind"].default == "hnsw"
    assert create.parameters["max_search_limit"].default == 1_000
    assert create.parameters["idempotency_key"].default is None
    assert inspect.signature(ContextNamespace.list_collections).parameters["limit"].default == 50
    assert (
        inspect.signature(ContextNamespace.wait_for_operation).parameters["timeout"].default
        == 1_800.0
    )
    assert inspect.signature(ContextNamespace.search).parameters["limit"].default == 10

    joint = inspect.signature(ContextNamespace.joint)
    assert joint.parameters["context_limit"].default == 50
    assert joint.parameters["seed_limit"].default == 8
    assert joint.parameters["graph_limit"].default == 200
    assert joint.parameters["traversal_limit"].default == 500
    assert joint.parameters["semantic_weight"].default == 0.7
    assert joint.parameters["lexical_weight"].default == 0.0
    assert joint.parameters["graph_weight"].default == 0.3

    point_mutation_union = {PointMutationResponse, ContextOperation}
    assert (
        set(get_args(get_type_hints(ContextNamespace.upsert_points)["return"]))
        == point_mutation_union
    )
    assert (
        set(get_args(get_type_hints(ContextNamespace.delete_points)["return"]))
        == point_mutation_union
    )
    assert get_type_hints(ContextNamespace.create_collection)["return"] is ContextOperation
    assert get_type_hints(ContextNamespace.search)["return"] is RankedResponse


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
        node
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "__all__" for target in node.targets)
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
