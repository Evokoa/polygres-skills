# MCP RAG pipeline

Read `mcp-tool-contract.md` first. Use MCP for interactive setup and verification;
use the SDK reference when the user needs persistent application code.

## Design

Record source ownership, authorization rules, stable source keys, citation
fields, freshness, and deletion behavior. Select one initial retrieval mode:

- `context_search` for semantic similarity
- `search_full_text` for lexical matching
- `context_text_hybrid_search` for semantic and text evidence
- graph-first, Context-first, rank fusion, or Joint for connected evidence

The caller owns embedding generation. Record model, revision, dimensions,
metric, document input, and query input.

## Configure

Inspect `get_context_capabilities`, discover the source, and run
`preflight_context_collection`. Include the collection request, source schema
effects, filters, point work, egress, and rollback in one review. After approval,
complete each server-issued confirmation and wait for durable operations.

Verify collection status and `verify_context_collection`. When graph contributes
to retrieval, use the graph playbook and verify its build independently.

## Retrieve and answer

Generate the query embedding outside Polygres when the chosen mode needs one.
Run one explicit retrieval tool with bounded candidates and result count.
Preserve source keys, scores, stage provenance, and request IDs. Resolve source
rows only when the current authorization and discovered tools support it.

Deduplicate by stable source identity, fit evidence to the application token
budget, and cite only returned records. Return an insufficient-evidence answer
when the results do not support the claim.

## Verify

Use a small labeled question set. Check collection readiness, useful citations,
authorization filtering, freshness, empty results, and latency before calling
the serving path operational.
