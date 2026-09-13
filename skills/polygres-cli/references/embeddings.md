# Managed embeddings

Use CLI 0.5.0 to generate embeddings from project text, keep them current, and
make them available for Context queries. Polygres stores generated records in
`polygres_embeddings`, preserving the source columns. The same workflow works
with synchronized text; continue writing source rows in the upstream database.

## Contents

- [Inspect the source and model](#inspect-the-source-and-model)
- [Preview and start](#preview-and-start)
- [Configure search](#configure-search)
- [Manage processing](#manage-processing)
- [Usage and recovery](#usage-and-recovery)
- [Remove a configuration](#remove-a-configuration)
- [Authentication and API fallback](#authentication-and-api-fallback)

## Inspect the source and model

Resolve identity and project before setup. Place global flags before the command:

```bash
polygres --json --project <project> embeddings sources
polygres --json --project <project> embeddings models
polygres --json --project <project> embeddings usage
polygres --json --project <project> embeddings list
```

Select an eligible table, one text column, and one of its `key_options`. A key
must identify every row uniquely and contain no null values. Preserve the order
and full set of columns for a composite key. Use the existing configurations to
avoid creating duplicate work.

Choose a model ID and supported dimensions from the returned catalog. Retain
its revision, source/query settings, input limit, and price version when
reviewing the choice. The saved configuration pins the model and dimensions;
trying another model means creating another configuration. Polygres manages
provider access and processing batch sizes.

To reuse an existing vector column, verify its original model, revision,
dimensions, and settings, then set `existing_vector_column` and
`confirm_original_model: true`. Matching vector dimensions alone is insufficient.
Compatible initial vectors are copied, and missing vectors are generated.
Subsequent text changes generate new managed vectors; changes only to the
original vector column do not replace managed output.

Chunking generates new vectors for each passage. Choose it for long documents,
with `overlap_tokens` smaller than `size_tokens`. Use generation without
`existing_vector_column` when chunking is enabled; whole-document vectors are
not reusable as passage vectors.

## Preview and start

Prepare `configuration.json` from the discovered source and selected catalog
model. Replace `MODEL_UUID` and the example dimensions with that model's values:

```json
{
  "name": "Article search",
  "source_schema": "public",
  "source_table": "articles",
  "source_key_columns": ["tenant_id", "id"],
  "source_text_column": "body",
  "model_id": "MODEL_UUID",
  "dimensions": 1536,
  "mode": "automatic",
  "use_credits": false,
  "chunking": {"enabled": false}
}
```

Both modes process the initial text. `automatic` processes subsequent changes
as they arrive; `manual` queues subsequent changes until `embeddings run`.

```bash
polygres --json --project <project> embeddings preview --file configuration.json
polygres --json --project <project> embeddings create --file configuration.json \
  --idempotency-key article-embeddings-v1
polygres --json --project <project> embeddings get <configuration-uuid>
```

Preview uses the create payload and returns source and sample counts, reusable
and missing sample rows, sample chunks, and token, storage, and additional
credit estimates. Explain when the estimate is sampled. Compare the estimated
usage with the generation allowance, authorized spending, available balance,
and cycle limit before starting. Create checks funding again before accepting
the configuration.

Obtain approval for the exact source, model, chunking, update mode, and credit
preference, using an existing approval when it already covers those choices.
`embeddings create` has no confirmation flag. Retain the returned configuration
ID and the explicit idempotency key. After an uncertain create outcome, replay
the unchanged payload with that key. `--file -` also accepts JSON from stdin.

## Configure search

```bash
polygres --json --project <project> embeddings context <configuration-uuid>
```

This command returns setup details; it does not create a collection. Use its
managed schema, table, source key, vector column, and dimensions to prepare an
`existing` Context collection. Carry over the suggested result columns, then
choose text search and filters for the application. Read [context.md](context.md)
for preflight, approved creation, and collection verification. Check generation
progress and the selected vector's index status separately.

For a dashboard handoff, open the project's **Embeddings** page and choose
**Generate embeddings** for setup or **Configure** in the saved configuration's
**Search collection** section. Use the CLI, SDK, or MCP to execute queries once
the collection is ready:

```bash
polygres --json --project <project> context search articles \
  --text "How does replication work?"
```

The collection's default vector selects the model binding. Use `--vector-name`
for another registered vector, as described in
[Context retrieval](context.md#choose-retrieval). Embedding configuration IDs
belong to the setup commands, not to search inputs.

## Manage processing

Inspect the latest `version`, `status`, `progress`, and `last_error_code` with
`embeddings get`. Use the action that matches the requested outcome:

```bash
polygres --json --project <project> embeddings pause <configuration-uuid>
polygres --json --project <project> embeddings resume <configuration-uuid>
polygres --json --project <project> embeddings run <configuration-uuid>
polygres --json --project <project> embeddings retry <configuration-uuid>
polygres --json --project <project> embeddings reconcile <configuration-uuid>
polygres --json --project <project> embeddings update <configuration-uuid> --file settings.json
```

Pause and resume control processing. Run requests pending work, including in
Manual mode. Retry schedules eligible work after its cause is resolved.
Reconcile checks earlier provider attempts and recovers saved results. It is
distinct from Context point reconciliation.

Update accepts `name`, `mode`, and `use_credits`, plus the current
`expected_version`. Example `settings.json`, using the version from the most
recent `get` response:

```json
{
  "expected_version": 1,
  "mode": "manual"
}
```

On a version conflict, fetch the configuration and review the intervening
change before submitting an updated request. Source columns, model,
dimensions, and chunking are fixed at creation. Batch sizing is managed by
Polygres and is not a create or update option.

Processing continues after the action response. Follow `embeddings get` for
completed source rows, pending work, recovery/retry details, and Context progress.
Polygres updates managed records and point mappings as text changes. Deletions
and empty text remove their search results; changed text becomes searchable
after its replacement embedding is ready.

## Usage and recovery

Read `embeddings usage` for separate `generation` and `query` allowances,
remaining and reserved amounts, model token counts, and `period_end`. Present
the returned allowance amounts and renewal dates, rather than hardcoding a
token quota. Costs depend on the model's current price binding and the tokens
actually processed. Reserved amounts cover work whose usage is still pending.

Keep total usage value, the portion covered by the included allowance, and
additional credit charges separate. API monetary values use microcredits:
1,000,000 microcredits equal one organization credit, worth US $0.01. Aggregate
fractional usage before describing whole-credit charges.

`use_credits` defaults to false for configurations and text queries. Additional
usage requires both this opt-in and an organization owner or administrator
enabling project spending with a positive limit per billing cycle. Inspect the
available balance, charged and reserved amounts, and remaining limit. Direct
spending changes to **Billing/Usage**; approval to configure embeddings does not
authorize changing the project's spending policy.

| Evidence | Next step |
| --- | --- |
| `EMBEDDING_QUOTA_EXHAUSTED` | Continue after renewal or obtain the required spending authorization. |
| `EMBEDDING_CREDIT_SPENDING_DISABLED` | Ask an organization owner or administrator to enable project spending if additional usage is wanted. |
| `EMBEDDING_CREDIT_LIMIT_EXCEEDED` or `CREDIT_INSUFFICIENT_BALANCE` | Review the cycle limit or organization balance before retrying. |
| `EMBEDDING_CONFIGURATION_CONFLICT` | Refresh the configuration and check its version or linked collections. |
| `EMBEDDING_SEARCH_NOT_READY` | Check the selected vector's binding, generation progress, collection, and index readiness. |
| Provider rate limit or temporary unavailability | Follow the returned retry guidance and preserve the current attempt. |
| `EMBEDDING_PROVIDER_OUTCOME_UNKNOWN` | Reconcile the attempt; retain its IDs if an administrator must confirm usage. |
| Model unavailable or provider credentials need attention | Retain the configuration and request IDs and contact support or an administrator. |

For query retries, retain the original text and idempotency key. A client timeout
does not establish whether generation completed. Let reconciliation resolve an
uncertain provider outcome before creating a new attempt.

## Remove a configuration

Read the latest version and identify any Context collections using the output.
Obtain approval for the configuration and the output choice:

```bash
polygres --json --project <project> embeddings remove <configuration-uuid> \
  --expected-version 1 --keep-output
```

`--keep-output` stops management and retains generated records. To remove those
records too, first remove their dependent Context collections with approval,
then use the latest version and `--delete-output`:

```bash
polygres --json --project <project> embeddings remove <configuration-uuid> \
  --expected-version 1 --delete-output
```

The two output flags are mutually exclusive and one is required. Source
columns and values are preserved with either choice. Removal has no `--yes`
flag; the explicit output choice is part of the reviewed command.

## Authentication and API fallback

The CLI uses the logged-in user and a project-scoped Runtime grant. Models,
usage, list, and get need `context:read`; source discovery, preview,
configuration changes, actions, and Context handoff need `context:manage`.

For an application that needs direct HTTP setup, use the documented project
Runtime URL and an authorized Runtime credential with the corresponding Context
permission. Public embedding routes are under `/embeddings`; use the actual
deployed OpenAPI contract and [the MCP tool contract](mcp-tool-contract.md) for
request details. `polygres api request` targets the central API and is not a
replacement for these Runtime commands. Keep provider credentials, model
administration, and private operator routes outside a user's project workflow.
