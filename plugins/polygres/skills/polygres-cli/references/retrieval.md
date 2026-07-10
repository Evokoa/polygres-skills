# Retrieval configuration

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

## Vector

```bash
polygres vector configs list
polygres vector configs create <name> \
  --table <table> \
  --embedding-column <column> \
  --dimensions <n> \
  [--schema public] \
  [--row-id-column id] \
  [--metric cosine|inner_product|l2] \
  [--index-kind hnsw|none]
polygres vector configs delete <config-id> [--yes]
polygres vector reindex <config-id>
```

Confirm dimensions match the stored embedding size. Metadata and filter columns
are repeatable flags. Delete accepts a configuration ID and requires approval.

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
