# MCP retrieval quality diagnosis

Read `mcp-tool-contract.md` first. Keep diagnosis read-only and preserve every
request ID.

Use `get_retrieval_readiness`, collection status and verification,
`get_context_diagnostics`, `get_context_index_status`,
`get_context_index_diagnostics`, `get_context_index_advice`,
`get_context_query_stats`, and `check_context_recall` as available.
Treat the `vector` and `hybrid` fields from `get_retrieval_readiness` as legacy
compatibility evidence only. They do not report Context readiness. A false
value is not a reason to recommend legacy vector setup, whose creation surface
is retired. Inspect Context capabilities, collections, collection status,
verification, and the selected named-vector index before claiming semantic
retrieval is unavailable.

When the requested diagnosis includes query evaluation, run a bounded labeled
query set with fixed candidate and answer limits. Text queries can generate
embeddings and use the project's query allowance. Check usage first, keep
`use_credits` false unless additional spending is authorized, and retain an
idempotency key for each distinct query. Measure
recall, precision, reciprocal rank, empty-result rate, latency, and truncation.
For hybrid retrieval, retain each stage's candidates, scores, and provenance.

For generated query embeddings, resolve the selected vector's configuration
and pinned model rather than choosing a model in the query. Each text nearest
branch in a query plan uses its own vector binding and query usage. See
[embedding diagnostics](embeddings.md) when generation or binding fails.

Check the embedding model and dimensions, query and document input formats,
filter registration and coverage, source freshness, point mappings, and
authorization. For graph, inspect status, relationship direction, depth,
fan-out, disconnected records, and build freshness. For full text, inspect
tokenization and configured text inputs.

Return the observed evidence and one smallest recommended improvement. Keep
reindex, reconciliation, graph build, and configuration changes as separate
approved actions routed to the appropriate operational skill.
