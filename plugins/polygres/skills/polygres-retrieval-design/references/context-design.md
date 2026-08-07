# pgContext design

Choose pgContext only after establishing that managed collection semantics add
value beyond a simple pgvector configuration.

## Data contract

Record:

- source schema, table, and exact `id` key semantics;
- `existing`, `add_column`, or `new_table` source mode;
- who owns the table, vector column, HNSW index, and embedding pipeline;
- embedding model, dimensions, metric, input construction, and update timing;
- text column, returned result columns, ordinary filters, and JSONB filter paths;
- expected row count, change rate, reconciliation frequency, and freshness SLO;
- whether authorization restricts collection choice or filter values.

Polygres does not generate embeddings. A non-empty existing source needs valid
native fixed-dimension Context vectors before registration. Do not propose
`add_column` for populated data without an explicit embedding and migration
plan.

## Retrieval mode

Choose the smallest mode that answers the representative questions:

- dense for semantic similarity;
- grouped search for per-key diversity;
- text hybrid when configured lexical evidence measurably helps;
- graph first when a trusted graph anchor defines the useful neighborhood;
- vector first when semantic seeds should acquire graph evidence;
- rank fusion when independent Context and graph ranks should be combined;
- Joint when graph expansion must introduce candidates before exact Context
  rescoring and final fusion;
- recall check for operational HNSW quality, not application retrieval.

Do not recommend graph composition without verified graph registrations, real
row IDs, useful relationships, bounded traversal, and a measurable benefit over
dense or text retrieval. A positive Joint lexical weight requires query text
and a configured text column.

## Lifecycle and validation

Plan capability discovery, source discovery, preflight, collection creation,
operation waiting, serving status, active verification, point synchronization,
diagnostics, reindex triggers, and deletion ownership.

Define how inserts, vector updates, source deletes, restores, bulk loads, and
embedding-model changes trigger point upsert, delete, reconciliation, or a new
collection. Include idempotency-key ownership and recovery after client
timeouts.

Validate with representative queries, exact dimension failures, empty and
non-finite embeddings, cosine zero vectors, unknown filter keys, tenant
isolation, text-column absence, graph capability absence, stale mappings,
recall thresholds, degraded status, and operation conflicts.

The current `context.v1` contract is preview. Record compatibility and fallback
behavior without implying automatic fallback to pgvector.
