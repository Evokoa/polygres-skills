# Errors and escalation

Use the public SDK exception hierarchy to classify failures:

| Exception | Likely boundary | Safe response |
| --- | --- | --- |
| `PolygresValidationError` | local request or response compatibility | correct validated input or SDK compatibility |
| `PolygresAuthError` | Runtime API authentication | verify credential source without exposing the API key |
| `PolygresPermissionError` | authorization | verify principal and policy; do not broaden access |
| `PolygresNotFoundError` | project resource or row identity | verify exact project, configuration, and row ID |
| `PolygresRateLimitError` | Runtime API rate limit | honor retry guidance and use a bounded retry |
| `PolygresRuntimeError` | Runtime API or transport response | preserve status, request ID, and sanitized details |

CLI parsing and local config failures occur before the remote control-plane.
Control-plane errors affect identity, project administration, or asynchronous
operations. Runtime API failures affect application retrieval. Database or
pooler failures should retain the sanitized Postgres error and SQLSTATE.

Escalate timeouts, contradictory readiness, repeated transient failures, or an
unknown partial failure with timestamps, CLI or SDK version, exact public
operation, affected project ID, `request_id`, job ID, and cursor. Redact all
credentials and user data not required to reproduce the issue. Recommend a
documented corrective action, but keep mutation in the appropriate
`$polygres-cli` or `$polygres-sdk` workflow after approval.
