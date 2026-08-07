# pgContext AI Search

## Contents

- [Boundaries](#boundaries)
- [Plan and preflight](#plan-and-preflight)
- [Create a collection](#create-a-collection)
- [Operate collections](#operate-collections)
- [Synchronize points](#synchronize-points)
- [Choose retrieval](#choose-retrieval)
- [Handle durable operations](#handle-durable-operations)
- [Delete safely](#delete-safely)

## Boundaries

Context is the pgContext-backed AI Search namespace. It is separate from
pgvector configurations and never accepts a vector configuration ID. Use
`polygres context capabilities`, not `polygres ready`, to establish effective
pgContext support and limits.

Polygres does not create embeddings. Confirm who generates embeddings, the
stored vector dimensions, the metric, and how new or changed source rows get
embedded before configuring a collection. Query embeddings must use the same
model and dimensions as stored source vectors.

Use collection UUIDs for collection administration, filters, points, and
operation-linked work. Count, facets, and ranked retrieval accept a UUID or an
exact collection name. Never fuzzy-match a collection name or infer the default
by scanning pages.

## Plan and preflight

Start with read-only evidence:

```bash
polygres --json context capabilities
polygres --json context sources discover --schema public
```

Choose one source mode:

- `existing`: register an existing table and native `pgcontext.vector(n)`
  column. Polygres does not own either object.
- `add-column`: add a native vector column to an empty existing table. This is
  a schema mutation and requires explicit approval.
- `new-table`: create a minimal source table. This is a schema mutation and
  requires explicit approval.

Preflight the exact create payload before mutation:

```bash
polygres --json context sources preflight --file collection.json
```

Report `eligible`, blockers, warnings, planned actions, and ownership
boundaries. Do not proceed past a blocker or treat a warning as verified safe.
Obtain explicit approval before every durable pgContext mutation. For
`add-column` or `new-table`, show the exact preflight DDL, affected schema
objects, and whether Polygres or the user owns each table, column, and index
before requesting approval.

## Create a collection

For an existing source:

```bash
polygres context collections create support_docs \
  --source existing \
  --schema public \
  --table documents \
  --source-key-column id \
  --vector-column embedding \
  --dimensions 768 \
  --metric cosine \
  --text-column content \
  --result-column title \
  --result-column url \
  --filter-column tenant_id \
  --filter-column category
```

Mutations generate an idempotency key and wait for the durable operation by
default. Use `--no-wait` only when the user wants acceptance without waiting.
Use an explicit stable `--idempotency-key` when recovery must survive a process
restart. A wait timeout does not cancel server work.

After creation, retain the operation and collection UUIDs and verify serving:

```bash
polygres --json context collections status <collection-uuid>
polygres --json context collections verify <collection-uuid>
```

A verification response can be HTTP-successful while `verified` is false.
Inspect the checks rather than treating the command exit alone as proof.

## Operate collections

Use public status and diagnostics before a mutation:

```bash
polygres --json context collections get <collection-uuid>
polygres --json context collections status <collection-uuid>
polygres --json context collections diagnostics <collection-uuid>
polygres --json context filters list <collection-uuid>
```

Register only filters required by known application queries. Ordinary columns
use `filters add-column`; JSONB fields use `filters add-jsonb-path`. Filter keys
are retrieval inputs, not an authorization boundary. Applications must derive
tenant filters from trusted authorization context.

Obtain approval before reindexing. Preserve the accepted operation ID and
verify status afterward.

## Synchronize points

Source rows and pgContext point mappings have separate lifecycles. Point status
is saved operational metadata, not a live comparison with the source table:

```bash
polygres --json context points status <collection-uuid>
```

Do not interpret `current` as proof that mappings match rows after out-of-band
changes. For known inserted or restored source keys, use `points upsert`. For
known deleted source keys, use `points delete`. Use `points reconcile` for bulk
loads or unknown row drift; it performs a live, full two-way reconciliation.
Updating an embedding vector does not by itself change the source-key mapping.

Small key batches may complete synchronously; larger accepted batches return
durable operations. Obtain approval before a durable point mutation and before
deleting mappings that affect serving behavior. Never resubmit after a timeout
until the existing operation has been checked.

Point scroll exposes mappings, not vectors or source payloads. Its cursor is
opaque and must be returned unchanged.

## Choose retrieval

Use aggregates when ranking is unnecessary:

```bash
polygres --json context count support_docs \
  --filter-json '{"must":[{"key":"tenant_id","match":"acme"}]}'
polygres --json context facets support_docs category --limit 10
```

`count` counts visible active points. `facets` aggregates a registered filter
key. Both accept a UUID or exact collection name and optional registered-filter
expressions.

Every ranked command requires a finite query embedding with the collection's
exact dimensions:

| Need | Command |
| --- | --- |
| Semantic similarity | `context search` |
| Results grouped by a registered filter | `context grouped-search` |
| Semantic plus configured full text | `context text-hybrid` |
| Start from a verified graph entity | `context graph-first` |
| Semantic seeds enriched with graph evidence | `context vector-first` |
| Independent Context and graph rankings | `context rank-fusion` |
| Coupled semantic, lexical, and graph candidates | `context joint` |
| Compare HNSW with exact retrieval | `context recall-check` |

Use real graph row IDs from trusted application data or prior results. Do not
invent start entities. `rank-fusion` and `joint` are different algorithms;
neither is an alias for the other. A positive Joint lexical weight requires a
query and a configured text column.

Ranked retrieval has no cursor. Only collections, operations, and point scroll
paginate. Preserve server order, warnings, scores, evidence, and request IDs.

## Handle durable operations

Inspect work without changing it:

```bash
polygres --json context operations list --collection-id <collection-uuid>
polygres --json context operations get <operation-uuid>
polygres context operations wait <operation-uuid> --timeout 1800
```

Cancellation and retry are separate durable mutations and require explicit
approval. Before retrying, inspect the operation. It must be failed or
cancelled, remain inside `retry_until`, and have attempts remaining; otherwise
the server rejects retry with a conflict. Retry creates a new operation; retain
both IDs. Interrupted waiting and client timeouts do not prove that the
operation failed or stopped.

## Delete safely

Read `context collections get` first and show the returned deletion plan.
Deletion removes the pgContext collection and verified Polygres-owned index but
preserves source tables, source columns, and user-created indexes.

Obtain explicit approval for the exact collection UUID before using:

```bash
polygres context collections delete <collection-uuid> --yes
```

Never add `--yes` based on prior approval for a different collection or
operation.
