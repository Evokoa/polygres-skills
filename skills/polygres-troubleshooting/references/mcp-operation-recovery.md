# MCP operation recovery

Read `mcp-tool-contract.md` first. Preserve the operation kind, operation ID,
project ID, request ID, last status, progress, error code, retryability, and
timestamp.

Use `get_operation` or the domain status tool to re-read current state. Treat
context, import, graph, and sync as distinct operation kinds. Use
`wait_for_operation` in bounded intervals and report the latest observed state
when its watch period ends.

Classify the failure as connection or OAuth, installation scope, current role
or project access, project mode or state, Central API, Runtime API, source
database, or durable operation execution. A tool missing from discovery can
indicate feature selection, read-only mode, scope, project compatibility, or
catalog version.

Recommend the smallest documented correction. After correction and explicit
approval, route supported actions as follows:

- `retry_operation` for a retryable Context operation
- `cancel_operation` for an eligible Context or import operation
- `retry_synchronization` for eligible synchronization state
- an exact Context reconciliation, graph build, or import restart through its
  normal workflow

Each action uses its own server proposal and returned digest. An ambiguous
row-write response remains a write-outcome investigation, not a failed durable
operation. Reuse its exact idempotency key only after public evidence supports
replay.
