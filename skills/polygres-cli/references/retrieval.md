# Retrieval configuration

## Contents

- [Graph](#graph)
- [Existing vector configurations](#existing-vector-configurations)
- [Text](#text)
- [General readiness](#general-readiness)

## Graph

```bash
polygres graph discover
polygres graph config export
polygres graph config apply --file graph.json
polygres graph build
polygres graph status
```

`graph discover` is read-only. `graph config apply` accepts a raw configuration
or an export wrapper with a non-null `configuration`. Review the full document
before applying. `graph build` invokes the backend build and can mutate index
state.

For a temporary table created solely to validate pgGraph, do not enable Row
Level Security or `FORCE ROW LEVEL SECURITY` unless the test explicitly targets
RLS behavior. Before reporting a pgGraph build failure, verify every registered
test table has both `relrowsecurity = false` and
`relforcerowsecurity = false`. If either flag caused the failure, classify it as
an incompatible test fixture, not a pgGraph product failure. Never disable RLS
on a pre-existing user table without explicit approval.

## Existing vector configurations

```bash
polygres vector configs list
polygres vector configs delete <config-id> [--yes]
polygres vector reindex <config-id>
```

Use these commands to inspect or maintain previously registered configurations.
For new semantic retrieval, start with `polygres context capabilities`, then use
`polygres context collections create` with a native `pgcontext.vector` column
or a compatible `public.vector` column that will be converted in place. The
older `polygres vector configs create` path is retired and returns
`VECTOR_CREATION_RETIRED`. Existing configurations remain listable, reindexable,
and removable. Legacy retrieval additionally requires a persisted enabled
registration that is effectively Ready. HNSW configurations require their exact
physical index to be Ready; an existing `index_kind: none` configuration can be
Ready for exact scan without HNSW. Never synthesize a configuration from an
unregistered physical index or claim the retired API can register or re-enable
it. Delete accepts a configuration ID and requires approval.

When migrating a registered pgvector column, preflight the intended Context
request, show the in-place type conversion and dependent-index impact, delete
the exact legacy registration with approval, then create and verify the native
collection. Do not use `context init` for this outcome; that command is the
guided onboarding front end for choosing one eligible persisted Legacy source
and submitting the same ordinary native collection-create request. Candidate
discovery requires the certified compatibility extension and a Ready physical
index; it cannot adopt a physical-only pgvector index. It does not activate an
internal same-column binding or preserve the old pgvector index.

## Text

```bash
polygres text configs list
polygres text configs create-fuzzy <name> \
  --table <table> \
  --text-column <column>
polygres text configs create-tsvector <name> \
  --table <table> \
  --tsvector-column <column>
polygres text configs create-tsvector <name> \
  --table <table> \
  --text-column <column> \
  --generated-column <column> \
  --yes
polygres text configs delete <config-id> [--yes]
```

Existing-column TSVector mode does not mutate the table. Generated-column mode
applies a migration and requires explicit approval before `--yes`. Fuzzy mode
uses an existing text-like column.

Text readiness is reported by `text configs list`. A configuration is usable
when its `index_status` is `ready`.

## General readiness

```bash
polygres ready
```

This reports graph, vector, and hybrid readiness. It does not report text
readiness in the current launch surface. Check text separately.

Polygres AI Context has its own capability, collection, point, operation, and
retrieval lifecycle. Use it for new semantic retrieval setup. Read `context.md`
from this skill when the request mentions Context, pgContext, AI Search,
collections, Joint retrieval, or point reconciliation. An existing pgvector
configuration is never itself a pgContext collection, even when its physical
column is eligible for in-place migration.
