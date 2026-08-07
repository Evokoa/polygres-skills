# pgContext

## Contents

- [Namespace and boundaries](#namespace-and-boundaries)
- [Capabilities and collection setup](#capabilities-and-collection-setup)
- [Identity and durable operations](#identity-and-durable-operations)
- [Point lifecycle](#point-lifecycle)
- [Choose retrieval](#choose-retrieval)
- [Authorization and result handling](#authorization-and-result-handling)

## Namespace and boundaries

Use the one synchronous namespace:

```python
context = client.project().context
```

Do not create collection handles, bound operations, an async client, or a
separate management client. Existing `project.graph`, `project.vector`,
`project.text`, and `project.hybrid` methods remain independent.

Context collections never accept pgvector configuration IDs. Polygres does not
generate source or query embeddings. The application owns the embedding model,
input construction, dimensions, update timing, and protection of any external
embedding credential. Query embeddings must match the collection dimensions
and metric requirements.

Use `$polygres-cli` for interactive collection setup and operator workflows.
Use SDK collection mutations only when the application deliberately owns
automated provisioning and the caller has the required management authority.

## Capabilities and collection setup

Use Context capabilities rather than general retrieval readiness:

```python
capabilities = project.context.get_capabilities()

if not capabilities.setup:
    raise RuntimeError(f"Context setup unavailable: {capabilities.setup_blocker}")
```

`setup` applies to collection setup. Before retrieval, check the capability for
the exact method the application will call. For example, require `dense_search`
for `search()` and `joint` for `joint()`, and surface the matching blocker:

```python
if not capabilities.dense_search:
    raise RuntimeError(
        f"Context search unavailable: {capabilities.dense_search_blocker}"
    )

if needs_joint_retrieval and not capabilities.joint:
    raise RuntimeError(f"Context Joint unavailable: {capabilities.joint_blocker}")
```

Use the corresponding `count`, `facets`, `grouped_search`, `recall_check`,
`text_hybrid`, `graph_first`, `vector_first`, or `rank_fusion` flag for those
methods. Collection status and verification do not replace feature-specific
capability checks.

Discover visible candidates, then preflight the exact collection request before
creating it:

```python
sources = project.context.discover_sources(schema_names=["public"])

source = {
    "mode": "existing",
    "schema_name": "public",
    "table_name": "documents",
    "source_key_column": "id",
}
vector = {
    "column_name": "embedding",
    "dimensions": 768,
    "metric": "cosine",
}

preflight = project.context.preflight(
    "support_docs",
    source=source,
    vector=vector,
    text_column="content",
    result_columns=["title", "url"],
    filter_columns=["tenant_id", "category"],
)

if not preflight.eligible:
    raise RuntimeError(f"Context preflight blocked: {preflight.blockers}")
```

Source modes are `existing`, `add_column`, and `new_table`. The latter two can
change database schema and should not be selected implicitly. Preflight is
read-only; successful preflight does not create or reserve a collection.

Create and verify only after blockers and ownership boundaries are accepted:

```python
operation = project.context.create_collection(
    "support_docs",
    source=source,
    vector=vector,
    text_column="content",
    result_columns=["title", "url"],
    filter_columns=["tenant_id", "category"],
    idempotency_key="support-docs-v1",
)
completed = project.context.wait_for_operation(operation)

if completed.collection_id is None:
    raise RuntimeError("Completed collection creation omitted collection_id")

status = project.context.get_collection_status(completed.collection_id)
verification = project.context.verify_collection(completed.collection_id)
if not verification.verified:
    raise RuntimeError(f"Context verification failed: {verification.checks}")
```

An HTTP-successful verification can still report `verified = False`. Inspect
the ordered checks and request ID.

## Identity and durable operations

Pass canonical collection UUIDs to administrative collection, filter, point,
and operation methods. Pass a UUID or exact collection name to count, facets,
and ranked retrieval. Do not scan collection pages to resolve names or infer a
default collection.

Every durable mutation returns immediately and sends one idempotency key. When
the key is omitted, the SDK generates one UUIDv4 and reuses it only for permitted
transport retries within that method invocation. Generated keys are not exposed
for later replay. Pass and persist a caller-owned stable key when recovery must
survive a failed call, a later call, or a process restart.

```python
operation = context.create_collection("support_docs", source=source, vector=vector)
completed = context.wait_for_operation(operation)
collection = context.get_collection(completed.collection_id)
```

Waiting is explicit, honors server retry guidance, and does not cancel on
timeout. Call `cancel_operation()` or `retry_operation()` separately when the
application intends that action. Never read a private operation result payload.

List and get operations to recover state after a process or network failure.
Only failed or cancelled operations are candidates for retry. The server also
enforces its attempt limit and the operation's `retry_until` window, so handle
`CONTEXT_OPERATION_NOT_RETRYABLE`. An accepted retry creates a new operation ID.
Preserve the original ID, replacement ID, collection ID, status, stage, error,
and request ID.

Collection deletion requires `confirm_collection_id` to exactly equal the path
collection UUID. Read the collection deletion plan first. Do not hide that
deletion is durable or imply that it deletes the source table.

## Point lifecycle

Source rows and Context point mappings have separate lifecycles. Upsert known
keys after inserts or vector changes, delete known keys after source deletion,
and reconcile after bulk or uncertain changes.

Commit the source-row transaction before calling `upsert_points()` or
`delete_points()`. The source database change and Context point mutation are not
one cross-system transaction. On an ambiguous outcome, inspect point status and
reconcile rather than assuming both sides committed together.

Point upsert and delete may return either `PointMutationResponse` or
`ContextOperation`:

```python
from polygres import ContextOperation

# The transaction that inserted or updated these source rows has committed.
result = project.context.upsert_points(
    collection_id,
    ["doc-1", "doc-2"],
    idempotency_key="support-docs-upsert-42",
)

if isinstance(result, ContextOperation):
    result = project.context.wait_for_operation(result)
```

Inspect `get_point_status()` before resubmitting after a timeout. Use
`scroll_points()` only for administrative point mappings; it does not expose
vectors or source payloads. Treat its cursor as opaque.

## Choose retrieval

| Need | Method |
| --- | --- |
| Count matching points | `project.context.count()` |
| Aggregate a registered filter | `project.context.facets()` |
| Semantic similarity | `project.context.search()` |
| Group by a registered filter | `project.context.grouped_search()` |
| Semantic plus configured full text | `project.context.text_hybrid()` |
| Expand from a verified graph anchor, then rank | `project.context.graph_first()` |
| Retrieve semantic seeds, then add graph evidence | `project.context.vector_first()` |
| Fuse independent Context and graph rankings | `project.context.rank_fusion()` |
| Couple semantic, lexical, and graph candidate generation | `project.context.joint()` |
| Compare HNSW results with exact retrieval | `project.context.recall_check()` |

Count and facet requests accept the same registered-filter shape as dense
retrieval. Facet only on a registered filter key:

```python
tenant_filter = {
    "must": [{"key": "tenant_id", "match": authorized_tenant_id}],
}
matching = project.context.count("support_docs", filter=tenant_filter)
categories = project.context.facets(
    "support_docs",
    "category",
    filter=tenant_filter,
    limit=20,
)
```

Dense retrieval uses a collection UUID or exact name:

```python
response = project.context.search(
    "support_docs",
    query_embedding,
    filter={
        "must": [
            {"key": "tenant_id", "match": authorized_tenant_id},
        ]
    },
    limit=10,
)
```

Use `graph_first()` when a verified start entity defines the candidate
neighborhood. Use `vector_first()` when semantic candidates should supply graph
seeds. Use `rank_fusion()` for independent rankings. Use `joint()` when graph
expansion must introduce candidates before exact Context rescoring and final
fusion. A positive Joint lexical weight requires a non-blank query and a
configured text column.

Do not invent graph IDs. Resolve starts from trusted application data or prior
typed results. Bound Context candidates, graph depth, graph candidates,
traversal candidates, final results, elapsed time, and application token use.

## Authorization and result handling

Registered filters constrain retrieval but are not an authorization boundary.
Derive collection choice and tenant filter values from trusted authorization
context. Do not pass arbitrary client-supplied tenant filters directly to
Context retrieval.

Ranked Context responses are typed envelopes, not cursor pages. Preserve server
order, scores, warnings, nullable fields, request IDs, and `to_dict()` output.
Administrative collection, point-scroll, and operation listings use `Page` and
opaque cursors.

`project.context.rank_fusion()` runs independent late fusion.
`project.context.joint()` calls only `/context/hybrid/joint` and preserves its
semantic, lexical, and graph evidence, contribution breakdown, fusion metadata,
trace counts, graph-introduction flag, baseline rank, and rank lift. It is not
an alias for rank fusion or `project.hybrid.joint()`.
