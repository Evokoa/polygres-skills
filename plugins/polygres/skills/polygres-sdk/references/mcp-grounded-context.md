# MCP grounded Context answers

Read `mcp-tool-contract.md` first. Use this playbook for an interactive grounded
answer when compatible MCP Context tools are available. Use the SDK references
for persistent Python application code.

1. Call `whoami` and resolve the project boundary.
2. Inspect `get_context_collection` and
   `get_context_collection_status`; use `verify_context_collection` when current
   serving evidence is required.
3. Read the collection's default vector, dimensions, metric, text inputs,
   result columns, filters, and source key contract.
4. Generate the query embedding outside Polygres for semantic retrieval.
5. Choose exactly one `context_search`, `search_full_text`,
   `context_text_hybrid_search`, `context_graph_first_search`,
   `context_first_graph_search`, `context_rank_fusion_search`, or
   `context_joint_search` call.
6. Bound candidates and final results. Apply authorization before retrieval;
   treat Context filters as retrieval narrowing rather than an authorization
   boundary.
7. Preserve source keys, scores, stage provenance, and request IDs. Resolve
   source rows only through an authorized discovered surface.
8. Deduplicate by stable source identity and fit the evidence to a stated token
   budget.
9. Cite only returned evidence. State that evidence is insufficient when the
   retrieved records do not support the answer.

Polygres returns evidence. The calling agent or application composes the answer.
