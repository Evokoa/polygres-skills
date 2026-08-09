# pgContext diagnostics

Confirm the installed Context command surface, then collect read-only evidence:

```console
polygres context --help
polygres --json --project <project> context capabilities
polygres --json --project <project> context collections get <collection-uuid>
polygres --json --project <project> context collections status <collection-uuid>
polygres --json --project <project> context collections verify <collection-uuid>
polygres --json --project <project> context collections diagnostics <collection-uuid>
polygres --json --project <project> context points status <collection-uuid>
polygres --json --project <project> context operations get <operation-uuid>
```

Do not use general `polygres ready` as proof of Context availability. Preserve
the capability blocker, collection and serving statuses, `vectors`,
`default_vector_name`, the requested `vector_name`, every vector's index status,
point reconciliation status, ordered verification checks, recommended
diagnostic actions, operation status and stage, error details, and every
request ID.

Also record whether the collection is the project default. That project-level
choice is independent of the collection's `default_vector_name`.

Classify likely causes:

| Evidence | Likely boundary |
| --- | --- |
| setup or search capability false | extension, Runtime schema, limits, or graph readiness |
| collection blocked or stale | source identity, index, point reconciliation, or prior operation |
| exact vector name not found | the request selected a vector not registered in that collection |
| one vector index not Ready | per-vector creation, ownership, index, or prior operation failure; do not generalize it to every vector |
| `CONTEXT_VECTOR_NULLABLE` during pgvector migration | at least one stored vector is `NULL`, not merely a nullable catalog declaration |
| `CONTEXT_VECTOR_DIMENSION_INVALID` during pgvector migration | discovered fixed dimensions and requested dimensions differ |
| `CONTEXT_INDEX_CONFLICT` during pgvector migration | a dependent index backs a database constraint and cannot be dropped safely |
| embedding invalid | empty, non-finite, wrong dimensions for the selected vector, or cosine zero vector |
| filter invalid | unregistered key or malformed public filter grammar |
| operation conflict | another durable mutation owns the collection or source resource |
| idempotency conflict | the key was reused for a different canonical request |
| recall `empty_exact` | exact retrieval found no comparison rows; this is distinct from a measured recall failure |
| recall unavailable or failing | missing verified HNSW attachment or measured recall below threshold |
| text hybrid unavailable | collection has no configured text column |
| graph or Joint unavailable | graph capability, registration, start identity, or configured limits |
| memory pressure or rate limit | admission boundary, not proof of collection corruption |

Check the existing operation before recommending a retry. A CLI wait timeout,
HTTP timeout, disconnect, or interrupted process does not prove that create,
reconcile, reindex, or deletion stopped. Retry is a mutation that creates a new
operation and requires approval.

For an ordinary create from `public.vector(n)`, verify the exact source column,
live `NULL` count, declared dimensions, dependent indexes, and constraint
ownership. The operation converts the column in place to native
`pgcontext.vector(n)` and does not preserve its old pgvector indexes. A
persisted Legacy registration must be deleted separately with approval; neither
dashboard creation nor direct creation performs that cleanup automatically. Do
not diagnose ordinary create as a same-column bridge.

For ranked retrieval, resolve the exact collection and selected vector first.
When `vector_name` was omitted, record the collection's
`default_vector_name`. Compare the embedding model and length with that
vector's dimensions, metric, and index status. A Ready sibling vector does not
make the selected vector Ready, and a failure in one vector does not prove the
whole collection is corrupt. Before diagnosing vector addition, inspect the
durable operation and confirm whether the requested mode was `existing` or
`add_column` and whether it requested a default-vector change.

Point status is saved last-known operational metadata, not a live source-table
comparison. For stale points, report whether the source changed and whether a
live reconciliation is needed. Do not run point upsert, delete, or reconcile
during diagnosis. Verification exposes `verified` and ordered checks; recall
check instead exposes recall state, counts, and measured recall. Do not invent a
verification-style boolean or checks for recall, and do not treat HTTP success
alone as a passing result.

Before diagnosing deletion, inspect `source_mode`, `owns_source_table`, and the
plural deletion-plan fields. `existing` and `add_column` preserve the source
table. A verified owned `new_table` source is dropped with its rows even if the
current summarized deletion plan says the table is preserved.

Escalate contradictory capabilities, repeated cross-tenant symptoms, lost
operation history, persistent resource locks, duplicate execution evidence, or
unknown source-identity mismatches with sanitized timestamps, exact project and
collection IDs, operation IDs, request IDs, CLI or SDK version, and observed
status. Never include embeddings, source payloads, API keys, or authorization
headers unless the minimum reproduction explicitly requires non-sensitive
sample data.
