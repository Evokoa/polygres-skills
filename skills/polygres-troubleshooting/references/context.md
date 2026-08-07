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
the capability blocker, collection and serving statuses, index status, point
reconciliation status, ordered verification checks, recommended diagnostic
actions, operation status and stage, error details, and every request ID.

Classify likely causes:

| Evidence | Likely boundary |
| --- | --- |
| setup or search capability false | extension, Runtime schema, limits, or graph readiness |
| collection blocked or stale | source identity, index, point reconciliation, or prior operation |
| embedding invalid | empty, non-finite, wrong dimensions, or cosine zero vector |
| filter invalid | unregistered key or malformed public filter grammar |
| operation conflict | another durable mutation owns the collection or source resource |
| idempotency conflict | the key was reused for a different canonical request |
| recall unavailable or failing | missing verified HNSW attachment or measured recall below threshold |
| text hybrid unavailable | collection has no configured text column |
| graph or Joint unavailable | graph capability, registration, start identity, or configured limits |
| memory pressure or rate limit | admission boundary, not proof of collection corruption |

Check the existing operation before recommending a retry. A CLI wait timeout,
HTTP timeout, disconnect, or interrupted process does not prove that create,
reconcile, reindex, or deletion stopped. Retry is a mutation that creates a new
operation and requires approval.

For stale points, report whether the source changed and whether status indicates
reconciliation is needed. Do not run point upsert, delete, or reconcile during
diagnosis. For a failed verification or recall threshold, report the boolean
result and checks; HTTP success alone is not a passing result.

Escalate contradictory capabilities, repeated cross-tenant symptoms, lost
operation history, persistent resource locks, duplicate execution evidence, or
unknown source-identity mismatches with sanitized timestamps, exact project and
collection IDs, operation IDs, request IDs, CLI or SDK version, and observed
status. Never include embeddings, source payloads, API keys, or authorization
headers unless the minimum reproduction explicitly requires non-sensitive
sample data.
