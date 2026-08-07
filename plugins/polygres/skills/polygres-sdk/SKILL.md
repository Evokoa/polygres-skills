---
name: polygres-sdk
description: Use the Polygres Python SDK to build application retrieval with pgContext, graph, vector, text, and hybrid queries; manage pgContext collections, points, and durable operations; configure safe Runtime API clients; paginate typed results; design grounded RAG context; and handle SDK errors. Use when writing, reviewing, testing, or troubleshooting Python backend code that calls a Polygres project Runtime API. Do not use for control-plane project administration, imports, migrations, or interactive CLI workflows.
---

# Polygres SDK

Build Python application code against the public `polygres-sdk` package and a
project's Runtime API. Use `$polygres-cli` instead for human authentication,
control-plane project administration, imports, migrations, and API-key management.

## Workflow

1. Inspect `pyproject.toml`, requirements files, and existing client setup.
2. Confirm that `polygres-sdk` is installed separately from `polygres-cli`.
   Follow the repository's package-manager policy and obtain approval before
   installing or changing dependencies.
3. Resolve `POLYGRES_API_KEY` and `POLYGRES_RUNTIME_URL` from server-side
   environment configuration. Never log or embed either value.
4. Confirm that the URL is the per-project Runtime API URL, not the Polygres
   control-plane URL or a direct or pooled Postgres URL.
5. Check `project.readiness()` before relying on legacy graph, vector, or hybrid
   retrieval. For pgContext, call `project.context.get_capabilities()` and then
   inspect collection status or verification. Use `project.connection_info()`
   only for passwordless connection metadata.
6. Keep every pgContext call on the flat `project.context` namespace. Prefer
   `$polygres-cli` for interactive setup. Use SDK mutations for explicit,
   backend-owned automation, return them immediately, and wait only when the
   application workflow requires a terminal result.
7. Choose one focused retrieval call. Use real row IDs returned by the SDK or
   verified application data; never invent graph identifiers.
8. Bound depth, candidate counts, result limits, pagination, and application
   token budget. Apply authorization before retrieval because filters are not
   an authorization boundary.
9. Preserve result provenance, request IDs, and typed models through RAG
   assembly. Deduplicate before constructing context.
10. Handle the documented exception hierarchy and test success, malformed
   responses, fuzzy or empty queries, invalid dimensions, and transient errors.

## Reference routing

- Read `references/client-setup.md` for installation, environment variables,
  endpoint selection, readiness, and passwordless connection information.
- Read `references/graph-retrieval.md` for graph calls, real row-ID discovery,
  direction, depth, and fan-out limits.
- Read `references/vector-and-text.md` for vector, TSVector, fuzzy retrieval,
  filters, thresholds, and vector dimension checks.
- Read `references/hybrid-and-rag.md` for graph-first, vector-first, joint
  retrieval, chaining, provenance, deduplication, and context budgets.
- Read `references/context.md` for pgContext collection identity, explicit
  operations, point lifecycle, retrieval modes, and Joint versus rank fusion.
- Read `references/errors-pagination-testing.md` for typed models, cursors,
  automatic pagination, exceptions, retries, and mocked tests.

## Boundaries

- Use only public SDK methods. Never reverse-engineer a private endpoint or
  private route, and never call the control-plane from application retrieval
  code.
- Use `project.context` for backend-owned pgContext collection configuration.
  Activate `$polygres-cli` for interactive human workflows and control-plane work.
- Do not pass pgvector configuration IDs to pgContext methods or imply that
  Polygres generates source or query embeddings.
- Never print headers, environment variables, API keys, or database secrets.
- Treat `connection_info()` as passwordless metadata. It does not return a
  database password.
- Do not claim a query is authorized merely because it includes filters.
- Do not retry validation, authentication, or permission errors blindly.
- Do not hide partial pagination, malformed payloads, timeouts, or request IDs.

## Completion report

State the Runtime API context without secrets, retrieval strategy, filters and
bounds, pagination behavior, provenance fields retained, tests run, and any
readiness or configuration work still required through `$polygres-cli`.
