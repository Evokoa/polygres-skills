# Context, embeddings, and retrieval

## Honor the embedding choice

Polygres does not generate source or query embeddings. Run
`scripts/check_embedding_device.py --json` only when semantic retrieval is
selected and the prompt or workspace does not already resolve a provider.
Supported choices include source-provided vectors; local Ollama, Sentence
Transformers, llama.cpp, ONNX, or another loopback adapter; a user-selected
hosted provider such as OpenAI; or no embeddings.

Follow `references/embedding-model-selection.md`. Inspect and rank silently.
Device feasibility does not imply that the user prefers local processing. If
deployment preference is unknown, normally include at most one local
recommendation and one hosted alternative in the existing consolidated review,
not in a separate question. Omit an inapplicable category. If the category is
already known, select an exact compatible model without another
embedding-specific question.

Obtain approval before installation, model download, or service startup. Pin
provider, model, revision, dimensions, normalization, document and query input
construction, batching, timeout, rate limits, egress, and cost. Hosted
processing requires explicit user choice or approval and credentials supplied
through named local environment variables. Never read credential values or
silently send content to a hosted endpoint. Use the identical contract for
indexing and querying.

## Configure pgContext correctly

For runtime capture into a Context-backed table, use one Context-backed rows
operation with an explicit collection or exact-one safe resolution. It writes
the source row and completes or starts the stable-ID point reconciliation.
Omit Context options for tables that are not selected for Context. Existing-row
backfills and deletion repair use the dedicated point lifecycle. A CLI bulk
import changes source rows only; when Context is selected, reconcile those rows
into Context and verify point readiness before claiming semantic retrieval or
the backfill is operational.

Use installed CLI help as the command source of truth. Inspect Context
capabilities, preflight the collection, review DDL, obtain approval, create or
update through `$polygres-cli`, wait for durable operations when needed, and
verify collection status before retrieval.

Do not mix embeddings with different models or dimensions in one named-vector
contract. Use a new named vector or reviewed reindex plan for model changes.

## Combine retrieval safely

- Relational: exact predicates, dates, joins, and counts.
- Text: exact terms, names, IDs, and error strings.
- Context: semantic similarity.
- Graph: explicit structural expansion.
- Hybrid: staged or Joint retrieval with provenance and deduplication.

Apply authorization before retrieval and again when resolving source rows.
Filters narrow candidates but are not the only authorization boundary.

## Define retrieval timing

For agent memory, a cheap recall check before meaningful prompts is a useful
default. Adapt timing to the host: recall may run before selected prompts, when
a router or agent requests it, after an explicit user command, or through the
application. Start with a small bounded result set such as 3 to 8 candidates,
then tune relevance, deduplication, and token budget from observed behavior.
Inject labeled source evidence and skip recall when the selected policy says it
adds no value.

For application retrieval, call the public SDK from server-side code. Preserve
source IDs, request IDs, pagination state, and partial results.

Use a documented Runtime API endpoint directly when the application language
cannot use the Python SDK. Follow the published authentication, request,
pagination, error, and idempotency contracts. Do not infer an endpoint from an
internal route or dashboard request.

## Degraded behavior

On a read outage, continue without memory only when approved and label degraded
mode. On a write outage, queue events only when a durable retry path exists.
Never claim queued data is stored. Keep exact or text fallback only when it was
approved and verified.
