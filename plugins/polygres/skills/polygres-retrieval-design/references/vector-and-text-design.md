# Vector and text design

## Existing vector retrieval

Apply this section to a previously registered vector configuration. New
vector-backed retrieval should be designed as a Polygres AI Context collection,
including its source mode, point reconciliation, filters, and verification.
Treat legacy retrieval as available only when the persisted registration is
enabled and its effective state is Ready. `index_kind` can be `none` or `hnsw`.
For `hnsw`, the exact configured physical index must be Ready. For `none`, a
verified registration can be Ready for exact-scan retrieval without an HNSW
index. A physical-only pgvector index is never implicitly registered or usable.
Do not design around registering or re-enabling one through the retired Legacy
APIs.

Record the embedding model, exact dimensions, distance metric, input template,
normalization, metadata columns, filters, result limit, minimum score,
`index_kind`, and, for `hnsw`, the exact physical index identity. Confirm that
stored and query embeddings use the same model and dimensions. Treat a
dimension mismatch, malformed vector, or empty embedding as a blocked input,
not a zero vector or retryable success.

For `hnsw`, state which source or index changes require a reindex and how exact
physical readiness is checked. For `none`, document exact-scan readiness and do
not invent an index build or reindex lifecycle. State what relational or text
fallback is safe while required retrieval resources are unavailable.
Plan tests for duplicate content, deleted rows, filter interactions, empty
queries, extreme lengths, and model-version compatibility mismatches.

## Text retrieval

For TSVector, record the source columns, weights, language configuration,
normalization, ranking, prefix behavior, and candidate cap. Test punctuation,
stop words, Unicode, empty input, and missing columns.

For fuzzy retrieval, record normalization, similarity threshold, indexed
columns, candidate cap, and an exact-match preference. Include noisy, short,
Unicode, and adversarial strings. Fuzzy matching is for user data, never to
fuzzy-match schema identifiers or silently select a project resource.
