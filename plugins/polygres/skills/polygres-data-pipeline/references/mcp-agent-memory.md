# MCP agent memory

Read `mcp-tool-contract.md` first. Define memory policy before creating storage.

Record owner, subject, tenant, source, stable identity, allowed content,
retention, deletion, freshness, and retrieval authorization. Exclude system
instructions, retrieved evidence, credentials, attachments, and tool output
unless the user explicitly includes them.

## Standard project

Use a stable event key and `validate_row_write`, then `upsert_row` for one
bounded memory record. Generate embeddings in the caller. Use
`upsert_context_points` or `reconcile_context_points` when the collection needs
an explicit mapping update. Preserve the same idempotency key when the write
result is ambiguous.

## Synchronized project

Write the memory record to the source PostgreSQL database. Use MCP Context or
Graph tools for retrieval after synchronization makes the record ready.

## Recall

Follow the grounded Context playbook: choose one retrieval mode, apply
authorization before and after retrieval, retain provenance, and fit results to
a bounded token budget. Never capture retrieved Polygres evidence as a new
source event.

## Integration

MCP is suitable for interactive capture and recall. Use the SDK with an outbox,
worker, or application hook when the user needs durable or retryable automation.
Agent instructions describe timing and content policy; runtime code provides the
delivery guarantee.
