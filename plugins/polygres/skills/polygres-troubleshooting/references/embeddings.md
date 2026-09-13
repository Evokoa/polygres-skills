# Embedding generation and query diagnostics

Use configuration, usage, and collection reads to locate the failing stage.
Generation and indexing have separate progress; a completed generation job
does not establish that the selected search index is ready.

## Contents

- [Collect public evidence](#collect-public-evidence)
- [Follow the source and selected vector](#follow-the-source-and-selected-vector)
- [Check the allowance and credit decision](#check-the-allowance-and-credit-decision)
- [Choose recovery by code](#choose-recovery-by-code)
- [Preserve uncertain outcomes](#preserve-uncertain-outcomes)

## Collect public evidence

Confirm CLI or SDK 0.5.0 for the new embedding inputs. With MCP, check tool
discovery, the Context feature, installation scopes, and project access.
`list_embedding_models`, `get_embedding_usage`,
`list_embedding_configurations`, and `get_embedding_configuration` need
`context:read`. Source discovery, preview, and Context handoff need
`context:manage`, including their read-only diagnostic use. See
[the MCP contract](mcp-tool-contract.md) for the complete tool catalog.

The equivalent CLI checks are:

```console
polygres embeddings --help
polygres --json --project <project> embeddings sources
polygres --json --project <project> embeddings models
polygres --json --project <project> embeddings usage
polygres --json --project <project> embeddings list
polygres --json --project <project> embeddings get <configuration-uuid>
polygres --json --project <project> embeddings context <configuration-uuid>
polygres --json --project <project> context capabilities
```

For setup validation, `preview_embeddings` or `embeddings preview --file` checks
the proposed configuration and estimates usage without calling the provider.
Preview can return sampled text, so retain only the fields needed for the
diagnosis. The estimate is not evidence that generation started.

Record the configuration ID and version, source table and key columns, source
text column, saved model ID and revision, dimensions, mode, `use_credits`,
`status`, `initial_scan_complete`, `last_error_code`, and progress. Distinguish
current `embedded_rows` and `pending_rows` from the cumulative `copied` and
`generated` work counters. Preserve `processing`, `retrying`, `next_retry_at`,
`failed`, `uncertain`, `context_pending`, and `context_failed` when relevant.

Use the dashboard's **Generate embeddings** entry point for setup, the
configuration's **Search collection** section for linked collection status,
and **Configure** for collection setup. Run query diagnostics through the
existing CLI, MCP, or SDK query methods. Keep processing batch size as returned
status information; updates accept name, mode, and credit opt-in with the
current `expected_version`. A source, model, dimension, or chunking change uses
a new configuration.

## Follow the source and selected vector

1. Check source discovery for a supported text column and a stable, non-null
   unique key. Match the saved column identities to the current source. Existing
   vectors require confirmation of their original model and compatible
   dimensions. Whole-row vectors cannot seed a chunked configuration.
2. Inspect generation status. Initial generation starts when the configuration
   is created, including Manual mode. Later Manual changes wait for an explicit
   run. Separate pending or delayed work from failed or uncertain work before
   recommending a retry.
3. Follow the Context handoff to the managed vector table and inspect its exact
   collection, serving status, point reconciliation, and selected vector index
   using [Context diagnostics](context.md). A collection linked to managed
   output follows that output; it is a different source from the original text
   table.
4. For a text query, check `query_embedding_generation` in Context capabilities.
   SDK 0.5.0 reports `CONTEXT_CAPABILITY_UNAVAILABLE` with that capability in
   `details` when the Runtime does not support it. An older CLI or missing MCP
   tool is a client or connection compatibility issue, separate from this
   Runtime capability.
5. Resolve `vector_name` exactly, or the collection's `default_vector_name` when
   it was omitted. The Runtime matches the vector's source table and column to
   one embedding configuration and checks its dimensions. The match can be the
   managed output or a confirmed original vector column. Matching dimensions
   alone do not identify a model. A missing or ambiguous match reports
   `EMBEDDING_SEARCH_NOT_READY`.
6. Compare the binding's saved model ID, revision, dimensions, and query settings.
   Text queries use that configuration; callers do not select a model in the
   query. Inspect the enabled model catalog for availability without changing
   an existing binding to a different model as a repair.

The SDK accepts text through its existing `project.context` retrieval methods,
and compatible existing `project.vector.search` and `project.hybrid` methods.
Keep `query` for lexical input where the method distinguishes it from semantic
`text`. Application-supplied vectors continue to bypass query generation.
Embedding configuration belongs in the dashboard, CLI, or MCP workflow.

For a synchronized project, check source sync freshness before embedding
progress, then check Context readiness. Polygres can generate managed output
from a synchronized text table. Correct source rows and schema in the source
PostgreSQL database; inspect managed output through its public configuration
and collection reads. Source capture, generation, and Context reconciliation
are three separate stages.

## Check the allowance and credit decision

Read the returned `generation` and `query` usage buckets separately. They are
monetary allowances measured in microcredits, not token-count quotas. Record
`included_microcredits`, `used_microcredits`, `reserved_microcredits`, and
`remaining_microcredits`, plus the returned `period_start`, `period_end`, and
`period_kind`. Per-model `input_tokens`, `price_version`, and
`microcredits_per_token` explain the cost. One credit is 1,000,000 microcredits
and USD 0.01. Use the returned period and balance instead of assuming a reset
date or deriving usage from row counts.

Additional usage needs all of the following: project credit spending enabled
by an organization owner or administrator, sufficient organization balance,
room within the project's cycle limit, and `use_credits=True` on the generation
configuration or query. The configuration's choice does not opt a query in.
Query opt-in defaults to `False`. Inspect `credit_spending_enabled`,
`cycle_credit_limit`, `charged_microcredits`, `reserved_microcredits`, and
`available_credit_microcredits`. An absent available balance is unknown, not
zero. Billing and usage in the dashboard provides the corresponding allowance
and spending controls.

Each text nearest branch in an executed query plan generates a query embedding
and uses the query allowance. Building the plan locally does not generate one.
A preview may show additional generation cost before setup; initial setup can
require the credit permission, opt-in, balance, and limit to cover that cost.

## Choose recovery by code

MCP exposes `error.code`, `error.message`, `error.retryable`, optional `variant`
and safe `details`, plus `request_id`. Use code and variant for classification
and the message for guidance. The retry classes below come from the public
error catalog; an HTTP status or SDK exception class alone is insufficient.

| Code | HTTP | Retry class | Next step |
| --- | --- | --- | --- |
| `EMBEDDING_SOURCE_INVALID` | 422 | `after_user_action` | Verify the discovered text column and stable unique key. |
| `EMBEDDING_SOURCE_CHANGED` | 409 | `after_user_action` | Compare current source identity with the saved configuration before proposing reconciliation. |
| `EMBEDDING_CONFIGURATION_NOT_FOUND` | 404 | `after_user_action` | Resolve the exact project and configuration ID. |
| `EMBEDDING_CONFIGURATION_CONFLICT` | 409 | `after_user_action` | Refresh the configuration version and review the intended change. |
| `EMBEDDING_SEARCH_NOT_READY` | 409 | `after_user_action` | Check generation, the selected vector's model binding, and its collection/index readiness. |
| `EMBEDDING_MODEL_INVALID` | 422 | `after_user_action` | Compare supported dimensions and input settings; escalate catalog setup issues to an administrator. |
| `EMBEDDING_MODEL_UNAVAILABLE` | 409 | `after_user_action` | Check model availability and escalate an existing binding that needs attention. |
| `EMBEDDING_INPUT_TOO_LONG` | 422 | `after_user_action` | Compare model and chunk limits; shorten a query or review source chunking. |
| `EMBEDDING_CHUNK_BOUNDARY_INVALID` | 422 | `after_user_action` | Review chunk size and overlap against the model's token limits. |
| `EMBEDDING_QUOTA_EXHAUSTED` | 429 | `after_user_action` | Check the affected allowance and authorized credit opt-in, or its returned renewal date. |
| `EMBEDDING_CREDIT_SPENDING_DISABLED` | 403 | `after_user_action` | Have the organization's billing administrator review project spending permission. |
| `EMBEDDING_CREDIT_LIMIT_EXCEEDED` | 409 | `after_user_action` | Review the project cycle limit, charged usage, and reservations. |
| `CREDIT_INSUFFICIENT_BALANCE` | 409 | `after_user_action` | Review available organization credits. |
| `EMBEDDING_PROVIDER_RATE_LIMITED` | 429 | `after_delay` | Honor retry timing; inspect scheduled work before proposing another attempt. |
| `EMBEDDING_PROVIDER_UNAVAILABLE` | 503 | `after_delay` | Inspect status and use bounded recovery after the provider becomes available. |
| `EMBEDDING_OPERATION_FAILED` | 503 | `after_delay` | Inspect the configuration and eligible work before proposing recovery. |
| `EMBEDDING_PROVIDER_REQUEST_REJECTED` | 422 | `after_user_action` | Review input limits and saved model settings. |
| `EMBEDDING_PROVIDER_CREDENTIALS_MISSING` | 503 | `after_user_action` | Escalate to a platform administrator with the model and request IDs. |
| `EMBEDDING_SERVICE_UNAVAILABLE` | 503 | `after_user_action` | Escalate the service availability evidence to a platform administrator. |
| `EMBEDDING_PROVIDER_OUTCOME_UNKNOWN` | 409 | `after_user_action` | Preserve the request identity and await verified provider usage reconciliation. |
| `EMBEDDING_USAGE_CONFLICT` | 409 | `after_user_action` | Compare the saved request identity and input before proposing another request. |

## Preserve uncertain outcomes

A lost response does not establish whether the provider consumed usage. Retain
the original query or creation idempotency key and exact input. Query retries
and pagination use the same key; each text branch in a query plan derives its
identity from the execution key. Changing a key creates a new request and can
consume additional usage.

Inspect `uncertain` progress and the public error before recommending recovery.
An administrator must verify uncertain provider usage before eligible work is
reconciled. The configuration's reconcile action does not verify provider
billing or repeat an unresolved provider call. After a recorded rejection or
reconciled query outcome, a fresh request may need a new key following the
confirmed correction. Do not automate that decision from a timeout alone.

Generation uses configuration status reads rather than generic Context
operation IDs. A separate Context setup or reconciliation operation has its
own status. Keep retry, resume, run, reconciliation, settings changes, and
removal in the authorized operational handoff; diagnosis itself remains read-only.
