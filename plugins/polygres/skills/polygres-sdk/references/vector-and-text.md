# Vector and text retrieval

## Existing vector search

Use `project.vector` only when the application already depends on a registered
vector configuration that remains enabled and is effectively Ready. An HNSW
configuration requires its exact physical index to be Ready; an existing
`index_kind: none` configuration can be Ready for exact scan without HNSW.
Polygres keeps those reads available for compatibility. A physical pgvector
index without that persisted registration is not implicitly usable, and the
legacy SDK/API cannot register or re-enable it. For new semantic retrieval
setup, use `project.context` and a Polygres AI Context collection instead of
attempting to create another vector configuration.

The embedding dimension must exactly match the selected configuration. Reject
empty embeddings, non-numeric values, infinity, and NaN locally. Do not pad,
truncate, or silently switch configurations.

```python
page = project.vector.search(
    embedding,
    config="documents_embedding",
    filters={"tenant_id": tenant_id},
    min_similarity=0.75,
    limit=20,
)
```

`max_distance` and `min_similarity` are alternative thresholds. Do not send
both. Evaluate threshold quality on representative data instead of presenting
one universal value.

Use an actual row ID for similarity search:

```python
page = project.vector.similar_to(
    result.id,
    config="documents_embedding",
    filters={"tenant_id": tenant_id},
    limit=10,
)
```

## TSVector search

Use the exact configured name and a non-empty query:

```python
page = project.text.tsvector(
    "postgres graph retrieval",
    config="documents_body_tsv",
    filters={"status": "published"},
    limit=20,
)
```

TSVector behavior depends on configured source columns and language. A missing
term can reflect stemming or configuration, not an unavailable row.

The SDK queries ready configurations but does not create, update, diagnose, or
reindex them. Route setup and maintenance through the dashboard, public API, or
CLI. Keep `cursor` opaque and reuse it only with the same configuration, query,
filters, and limit that produced it.

## Fuzzy search

Fuzzy retrieval is useful for typos and approximate text, not semantic meaning:

```python
page = project.text.fuzzy(
    "postgress",
    config="documents_title_fuzzy",
    limit=10,
)
```

Reject an empty or whitespace-only query. Test short strings, punctuation,
Unicode, transpositions, repeated characters, and unrelated terms. A fuzzy
match is evidence to rank or present, not permission to silently replace user
data or select an ambiguous resource.

For a compound row key, read every value from `result.key`. Keep using
`result.id` for existing single-key integrations. A filter value of `None`
intentionally matches SQL `NULL`; omit a filter when no filtering is intended.

## Filters and authorization

Filters narrow retrieval but do not replace authorization. Resolve the user's
tenant and permissions before querying, constrain filters with trusted values,
and verify the returned rows are still authorized. Do not allow arbitrary input
to overwrite required tenant or ownership filters.
