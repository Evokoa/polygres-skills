# Errors, pagination, and testing

## Exception handling

Catch the narrowest useful SDK exception:

- `PolygresValidationError`: correct malformed local input; do not retry.
- `PolygresAuthError`: replace or rotate server-side credentials; do not log
  them.
- `PolygresPermissionError`: stop and correct authorization or project scope.
- `PolygresNotFoundError`: verify the exact resource or real row ID.
- `PolygresRateLimitError`: honor retry guidance and back off.
- `PolygresRuntimeError`: preserve the `request_id`; retry only when the
  operation is safe and within the application's bounded retry policy.

```python
from polygres import PolygresRateLimitError, PolygresRuntimeError

try:
    page = project.vector.search(embedding, limit=10)
except PolygresRateLimitError as error:
    logger.warning("Polygres rate limited request_id=%s", error.request_id)
    raise
except PolygresRuntimeError as error:
    logger.error("Polygres runtime failure request_id=%s", error.request_id)
    raise
```

Do not include request headers or environment values in logs. A timeout is not
proof that no response or server work occurred.

## Pagination

Process one page when latency and a fixed result cap matter:

```python
page = project.text.tsvector(query, config="documents_body_tsv", limit=25)
for result in page.results:
    consume(result)
next_cursor = page.next_cursor
```

Use `.auto_paging_iter()` only when the application genuinely needs all pages:

```python
page = project.vector.search(embedding, config="documents_embedding", limit=100)
for result in page.auto_paging_iter():
    consume(result)
```

Set an application maximum for rows, pages, elapsed time, and context tokens.
Preserve the last cursor and request ID when stopping early or after a partial
failure.

## Typed results

Prefer the exported typed models (`GraphResult`, `VectorResult`, `TextResult`,
`HybridResult`, `GraphPathResponse`, `GraphConnectionResponse`, and `Page`) over
guessing dictionary shapes. Use `to_dict()` only at serialization boundaries.
`Project` and the graph, vector, text, and hybrid namespace classes are not
exported from `polygres`; do not import them for application annotations. Use
type inference or an application-owned `Protocol` for dependency injection.

## Focused tests

Mock the Runtime API transport and assert the request path, payload, headers
without secret values, typed response, cursor propagation, and exception type.

```python
def test_empty_vector_results_are_handled(mock_runtime, client):
    mock_runtime.respond(json={"results": [], "has_more": False})

    page = client.project().vector.search([0.1, 0.2], limit=5)

    assert page.results == []
    assert page.has_more is False
```

```python
def test_malformed_runtime_payload_is_not_treated_as_success(mock_runtime, client):
    mock_runtime.respond(json={"results": [{"distance": "not-a-number"}]})

    with pytest.raises((KeyError, TypeError, ValueError)):
        client.project().vector.search([0.1, 0.2])
```

Cover empty pages, malformed JSON payloads, missing fields, invalid dimensions,
NaN and infinity, whitespace-only and fuzzy text, bad directions, depth and
limit boundaries, 401, 403, 404, 429, 5xx, network errors, timeout after
retries, multi-page cursors, and partial iteration failure.
