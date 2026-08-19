# Managed PostgreSQL sync projects

## Choose managed sync only when it fits

Choose a synced project for an eligible Supabase, Neon, or PostgreSQL source
when the source must remain the system of record and a new Polygres project is
acceptable. Use a standard project and a custom pipeline when the workflow
requires target SQL, target row writes, imports, migrations, a non-PostgreSQL
source, or tables that fail the sync preflight.

Do not describe sync as a conversion of an existing standard project. Create a
new synced project through `polygres projects create sync` or the dashboard.

## Keep credentials out of agent-visible paths

Prefer the CLI's hidden interactive source-URL prompt, or direct the user to
**New project** in the dashboard. For non-interactive CLI creation, reference a
user-populated environment variable with `--connection-env`; never inspect its
value. Never request, record, or pass the source URL or password through chat, a
plan, generated files, logs, literal CLI arguments, the Runtime API, or the SDK.
A direct PostgreSQL endpoint is required; do not use a pooler URL, provider API
URL, `psql` command, or publishable key.

Treat the source inspection result from CLI creation or the dashboard as
authoritative. It checks supported PostgreSQL versions, network and TLS access,
authentication, logical replication, publication and replication privileges,
slot capacity, storage, and eligible sync keys. Current managed sync selects
eligible tables in the `public` schema. Polygres creates the filtered
publication and replication slot only after final admission.

## Model a synced setup

Record `target.project_mode: synced`, `source.system_of_record`, and a
`sync.mode` of `managed-postgres`. Record only non-secret provider and selected
table or column scope. Represent initial creation with a `cli` or `dashboard`
interface. Use `dashboard` for later selection reconfiguration and lifecycle
actions because those commands are not exposed by CLI 0.4.0.

Do not select or scaffold:

- target schema creation or alteration;
- CLI import, Runtime rows, or SDK rows;
- target database credentials, SQL, or `psql`;
- a custom CDC worker, backfill writer, or checkpoint ledger.

Use the project Runtime API key only for supported retrieval and retrieval
configuration. It cannot create or control sync and cannot access rows,
imports, migrations, or database connection information.

## Write and enrich at the source

Write, update, delete, and generate embeddings in the source database. Managed
snapshot and logical replication carry eligible changes into Polygres. For a
Context collection, use an existing synchronized table and column; do not plan
`new_table` or `add_column` on the target. Polygres does not generate
embeddings.

Use graph relationships only when both foreign-key endpoint tables are in the
selected sync scope. Treat exact SQL and transactional joins as source-database
work. Use Polygres graph, text, vector, hybrid, Context, and readiness surfaces
for retrieval.

## Reconfigure and recover safely

Refresh source inspection before changing selected tables. Use the current
configuration generation as the compare-and-set boundary. Added or materially
changed tables enter resync; deselected tables stop syncing. Re-check retrieval
configuration when selected tables, columns, stable keys, or embeddings change.

Read lifecycle state and `valid_actions` from the control plane instead of
inferring actions locally. Initial setup moves through provisioning, syncing,
and ready; nested states include initializing, snapshotting, catching up,
streaming, resyncing, paused, and failed. Treat resnapshot as destructive to
the mirrored target and disclose it before approval.

Do not promise source credential rotation as a self-service workflow. The
dashboard currently hides it because replacing an active capture credential is
not reliably supported.
