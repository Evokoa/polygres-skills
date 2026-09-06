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

Run a bounded labeled query set with fixed candidate and answer limits. Measure
recall, precision, reciprocal rank, empty-result rate, latency, and truncation.
For hybrid retrieval, retain each stage's candidates, scores, and provenance.

Check the embedding model and dimensions, query and document input formats,
filter registration and coverage, source freshness, point mappings, and
authorization. For graph, inspect status, relationship direction, depth,
fan-out, disconnected records, and build freshness. For full text, inspect
tokenization and configured text inputs.

Return the observed evidence and one smallest recommended improvement. Keep
reindex, reconciliation, graph build, and configuration changes as separate
approved actions routed to the appropriate operational skill.
