# Retrieval diagnostics

Collect only supported public readiness and configuration evidence:

```console
polygres --json --project <project> graph status
polygres --json --project <project> vector configs list
polygres --json --project <project> text configs list
polygres --json --project <project> ready
```

Application code may call `$polygres-sdk` `project.readiness()` to obtain the
same class of public evidence. Preserve returned typed fields and request IDs.

For a graph build issue, compare readiness and configuration identity, then
check exact node table, stable row ID, direction, bounded depth, and empty
results. For a vector reindex issue, verify configuration identity, embedding
model and dimensions; a dimension mismatch or empty embedding is an input or
compatibility error, not evidence that a retry will help. For TSVector or fuzzy
results, inspect exact configured columns, language or threshold, normalization,
and empty queries.

For hybrid requests, identify the failing stage and preserve provenance. A
partial failure in graph expansion after vector candidates is not a successful
hybrid result. If SDK pagination exposes a cursor, retain it and distinguish a
complete result set from a partial page. Never start a rebuild or reindex while
diagnosing.
