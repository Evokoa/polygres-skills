# Errors and escalation

Use the public SDK exception hierarchy to classify failures:

| Exception | Likely boundary | Safe response |
| --- | --- | --- |
| `PolygresValidationError` | local request or response compatibility | correct validated input or SDK compatibility |
| `PolygresAuthError` | Runtime API authentication | verify credential source without exposing the API key |
| `PolygresPermissionError` | authorization | verify principal and policy; do not broaden access |
| `PolygresNotFoundError` | project resource or row identity | verify exact project, configuration, and row ID |
| `PolygresRateLimitError` | rate limit or embedding allowance | classify by `code`; provider throttling can recover after a delay, while allowance exhaustion needs a usage or funding decision |
| `PolygresMaintenanceError` | declared service maintenance | stop normal retries and honor supplied retry guidance |
| `PolygresRuntimeError` | Runtime API or transport response | preserve status, request ID, and sanitized details |
| `PolygresAPIError` | other public API failure | preserve status, code, details, and request ID |

CLI parsing and local config failures occur before the remote control-plane.
Control-plane errors affect identity, project administration, or asynchronous
operations. Runtime API failures affect application retrieval. Database or
pooler failures should retain the sanitized Postgres error and SQLSTATE.

For embedding generation or text queries, use [embedding diagnostics](embeddings.md)
to distinguish model binding, source or index readiness, monetary allowances,
and provider availability. `EMBEDDING_PROVIDER_OUTCOME_UNKNOWN` requires verified
usage reconciliation before another attempt. Preserve the query idempotency key
alongside the request ID after a transport timeout.

An MCP tool error contains `error.code`, `error.message`, `error.retryable`,
optional `error.variant` and safe `error.details`, and `request_id`. Classify by
code and variant, and use the catalog-owned message as guidance. HTTP 429 by
itself does not establish that a retry is appropriate.

Escalate timeouts, contradictory readiness, repeated transient failures, or an
unknown partial failure with timestamps, CLI or SDK version, exact public
operation, affected project ID, `request_id`, job ID, and cursor. Redact all
credentials and user data not required to reproduce the issue. Recommend a
documented corrective action, but keep mutation in the appropriate
`$polygres-cli` or `$polygres-sdk` workflow after approval.
