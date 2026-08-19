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

For TSVector, choose either an existing compatible `tsvector` column or a
stored generated column built from one or more text source columns. Record the
source columns, generated-column ownership, language configuration,
normalization, ranking, prefix behavior, metadata columns, filter columns,
stable single or compound row key, default limit, and maximum limit. Generated
setup uses the existing text configuration endpoint and does not require a
separate migration. PostgreSQL keeps the stored generated value current when a
source column changes. Plan diagnostics and reindexing for physical-index
failure, and state that deleting the configuration does not drop the generated
table column. Test punctuation, stop words, Unicode, empty input, missing
columns, null filters, and cursor reuse with changed query inputs.

For fuzzy retrieval, record normalization, similarity threshold, indexed
columns, default and maximum limits, metadata and filter columns, stable row
key, and an exact-match preference. Include noisy, short, Unicode, and
adversarial strings. Fuzzy matching is for user data, never to fuzzy-match
schema identifiers or silently select a project resource.
