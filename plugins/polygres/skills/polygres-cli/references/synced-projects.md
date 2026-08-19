# Synchronized PostgreSQL projects

## Resolve project mode first

Read `project_mode` from project list, selection, or status output before using
a database or mutation command. Treat an omitted mode from an older response as
`standard`; only the authoritative value `synced` activates this boundary.

The CLI can list, select, and inspect a synced project and can use supported
retrieval commands after the project is ready. It has no first-class command to
create a synced project, run source preflight, select or reconfigure source
tables, or perform sync lifecycle actions. Direct the user to the dashboard for
those operations.

Do not use generic `polygres api request` as a sync workflow. Do not place a
source connection URL or password in a CLI body, argument, file prepared for an
agent, or terminal transcript.

## Enforce the unavailable surfaces

Do not run these commands on a synced project:

- `polygres db info` or `polygres db psql`;
- `polygres env` for target database information;
- `polygres rows validate`, `insert`, `upsert`, or `ignore`;
- `polygres import ...`;
- `polygres migrations ...`.

Do not use rows validation as a capability probe. The Runtime rejects these
surfaces with `SYNCED_PROJECT_SURFACE_UNAVAILABLE`. This is an intentional
permission boundary, not a transient failure. Write, update, delete, and create
embeddings in the source database instead.

The installed CLI may reject `db` and `env` locally before starting a database
client. Older CLI versions can rely on the server boundary for other
unsupported surfaces. Follow installed `--help` and the current skills release
compatibility record; do not claim a local guard exists in a version where it
has not been released.

## Use the restricted Runtime key

`polygres keys create` issues the synced-project key profile automatically for
a synced project. The secret is for trusted server-side Runtime calls only. It
does not authenticate dashboard or control-plane sync operations and cannot be
used for rows, imports, migrations, SQL, or database connection information.

Allowed Runtime surfaces are graph, text, existing vector, hybrid, Context,
retrieval readiness, and the table catalog. Keep Context creation on an
existing synchronized table and column. Do not choose `add-column` or
`new-table`; generate and persist embeddings in the source database.

## Interpret sync status

Report the observed project and nested sync state. Do not infer a lifecycle
action from state alone; use the server-provided `valid_actions`. Creation can
move through provisioning, syncing, and ready, while nested states include
initializing, snapshotting, catching up, streaming, resyncing, paused, and
failed.

The dashboard supports selected-table reconfiguration after re-inspection.
Added or changed tables resync and deselected tables stop syncing. Do not
promise source credential rotation as a self-service operation because the
dashboard currently hides it.
