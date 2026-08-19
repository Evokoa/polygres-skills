# Synchronized PostgreSQL project diagnosis

## Establish the boundary without secrets

Confirm `project_mode: synced` from public project output. Record project
status, sync state, desired state, failure stage, pause reason, configuration
generation, table states, lag, and server-provided `valid_actions`. Never
request, print, or reconstruct the source connection URL or password.

Do not run `db info`, `db psql`, target SQL, rows validation, imports, or
migrations. `SYNCED_PROJECT_SURFACE_UNAVAILABLE` from one of those surfaces is
expected enforcement, not evidence of a sync outage.

Separate these boundaries:

- CLI or dashboard control plane: initial creation, source inspection, and
  selection; dashboard control plane: later lifecycle and reconfiguration;
- source PostgreSQL: connectivity, privileges, schema, keys, and source writes;
- Runtime API: supported graph, text, vector, hybrid, Context, catalog, and
  readiness operations.

## Diagnose preflight

Use the stable public result code and sanitized details. Common source failures
include:

- `SOURCE_URL_INVALID`, `SOURCE_DESTINATION_BLOCKED`,
  `SOURCE_NETWORK_UNREACHABLE`, and `SOURCE_IPV4_ADDRESS_MISSING`;
- `SOURCE_TLS_REQUIRED` and `SOURCE_AUTH_FAILED`;
- `SOURCE_VERSION_UNSUPPORTED` and `SOURCE_WAL_LEVEL_NOT_LOGICAL`;
- `SOURCE_PUBLICATION_PRIVILEGE_MISSING` and
  `SOURCE_REPLICATION_PRIVILEGE_MISSING`;
- `SOURCE_SLOT_CAPACITY_EXHAUSTED` and
  `SOURCE_CATALOG_INSPECTION_FAILED`;
- `SYNC_KEY_UNAVAILABLE`, `TABLE_KIND_UNSUPPORTED`,
  `TABLE_NAME_UNSUPPORTED`, and `PARTIAL_TABLE_COLUMNS_OMITTED`;
- `SYNC_SELECTION_EMPTY`, `SYNC_SELECTION_INVALID`, and
  `SYNC_SELECTION_OVER_TIER_LIMIT`;
- `SYNC_PREFLIGHT_BACKEND_UNAVAILABLE` and `SYNC_PREFLIGHT_NOT_ADMITTED`.

Check that the user supplied a direct PostgreSQL endpoint rather than a pooler,
provider API URL, `psql` command, or publishable key. Current managed sync
selects eligible tables in `public`. Treat the preflight response as
authoritative for column and sync-key eligibility.

## Diagnose lifecycle and table state

Distinguish provisioning, syncing, and ready from nested initializing,
snapshotting, catching up, streaming, resyncing, paused, and failed states.
Check the recorded failure stage before recommending an action.

For an initial snapshot or catch-up issue, inspect per-table progress and lag.
For ongoing streaming, inspect source changes, lag trend, schema drift, storage
pressure, stream capacity, poison transactions, and table-specific errors.
Preserve errors such as `SYNC_SCHEMA_DRIFT_DETECTED`,
`SYNC_TRANSACTION_TOO_LARGE`, or `SYNC_TARGET_APPLY_FAILED` without inferring a
private infrastructure cause.

For selection changes, refresh status and generation before diagnosis.
`SYNC_CONFIGURATION_GENERATION_CONFLICT` or
`SYNC_SELECTION_GENERATION_CONFLICT` means the client acted on stale state.
Added or changed tables can be `resyncing`; deselected tables stop syncing.

## Recommend only currently valid recovery

Re-read `valid_actions` immediately before recommending pause, resume, retry,
resnapshot, or delete. Do not execute a repair while diagnosing. Treat
resnapshot as destructive to mirrored target state and require an explicit
review before handoff.

Do not recommend self-service source credential rotation. The dashboard
currently hides it because reliable active-capture replacement is not yet a
supported user workflow.

After sync is healthy, diagnose retrieval readiness separately. A streaming
sync does not prove a Context collection, graph build, text configuration, or
existing vector configuration is ready.
