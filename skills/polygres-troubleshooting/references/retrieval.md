# Retrieval diagnostics

Collect only supported public readiness and configuration evidence:

```console
polygres --json --project <project> graph status
polygres --json --project <project> vector configs list
polygres --json --project <project> text configs list
polygres --json --project <project> text configs get <config-id-or-name>
polygres --json --project <project> text configs diagnostics <config-id-or-name>
polygres --json --project <project> ready
```

Application code may call `$polygres-sdk` `project.readiness()` to obtain the
same class of public evidence. Preserve returned typed fields and request IDs.

The vector configuration command is diagnostic support for existing
registrations. New semantic retrieval setup belongs under Polygres AI Context;
use the Context diagnostic workflow when collection creation or serving is
involved. For a legacy query, confirm that the exact persisted registration is
enabled and effectively Ready. HNSW requires its exact physical index to be
Ready; an existing `index_kind: none` configuration can be Ready for exact scan
without HNSW. An unregistered physical pgvector index is not a usable fallback
and cannot be registered or re-enabled through the retired API.

For a graph build issue, compare readiness and configuration identity, then
check `relrowsecurity` and `relforcerowsecurity` for every registered temporary
test table before attributing the failure to pgGraph. A temporary pgGraph
fixture must leave both flags false unless the test explicitly targets RLS. If
RLS caused the failure, report a fixture/setup incompatibility rather than a
pgGraph defect. Do not recommend disabling RLS on a pre-existing user table
without explicit approval. Then check exact node table, stable row ID,
direction, bounded depth, and empty results. For a vector reindex issue, verify
configuration identity, embedding model and dimensions; a dimension mismatch
or empty embedding is an input or compatibility error, not evidence that a
retry will help.

For TSVector or fuzzy failures, resolve one exact configuration by ID or name.
Compare `index_status` and `index_error` with diagnostic `healthy`,
`index_found`, `index_valid`, and `index_ready`. Inspect the exact table,
compound row key, TSVector or text column, language or similarity threshold,
metadata columns, filter columns, and limits. An empty query is invalid. A
filter key must be registered, and a null filter intentionally matches SQL
`NULL`.

Generated TSVector setup uses the existing configuration endpoint, not a
migration. If `TEXT_GENERATION_CLEANUP_FAILED` is reported, inspect the table,
managed index, and saved configuration before recommending another attempt. Do
not run `text configs reindex` while diagnosing. After the target is corrected,
route that mutation through `$polygres-cli` with explicit approval.

For hybrid requests, identify the failing stage and preserve provenance. A
partial failure in graph expansion after vector candidates is not a successful
hybrid result. If SDK pagination exposes a cursor, retain it and distinguish a
complete result set from a partial page. Never start a rebuild or reindex while
diagnosing.
