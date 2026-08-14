# Changelog

All notable changes to Polygres Agent Skills are documented in this file.

## 0.4.0 - 2026-08-14

### Added

- Added `polygres-data-pipeline` for guided ingestion and retrieval setup from
  conversations, databases, files, APIs, event streams, and existing Polygres
  data.
- Added read-only device inspection and user choice for local Ollama, Sentence
  Transformers, llama.cpp, and application-owned ONNX embedding options.
- Added a versioned pipeline-plan validator, setup-pack scaffolder, safe `.env`
  status checker, local embedding adapters, and an idempotent SQLite checkpoint
  ledger.
- Added separate documented store and retrieve interface decisions for CLI,
  SDK, Runtime API, and approved direct Postgres fallback workflows.
- Added a versioned local and hosted embedding model catalog plus deterministic,
  device-aware recommendation tooling.

### Changed

- Expanded the plugin from four skills to five.
- Added one-line setup prompts such as `Look at my data and use
  $polygres-data-pipeline to set up a Polygres data pipeline.`
- Required generated local setup packs to ignore `.env`, keep credential values
  out of agent context, and give the user exact local paste instructions.
- Changed pipeline setup to a bounded build-first fast path. The skill creates
  and tests source-specific runtime code before full source inspection,
  backfill, or broad Polygres capability discovery.
- Limited questions to genuine blockers and consolidated upload and remote
  mutation approval into one review.
- Updated CLI and SDK guidance for the single-row Runtime write surface,
  including exact no-retry behavior and ambiguous outcomes.
- Made Context-backed capture one user-facing row operation that also completes
  or durably starts point reconciliation.
- Defined per-surface checkpoint state for pending or partially failed Context
  reconciliation, with exact idempotent replay instead of a manual point step.
- Preserved generic row-only behavior unless a Context collection is explicitly
  selected or resolved safely.
- Moved an unknown local-versus-hosted embedding choice into the single setup
  review, so selecting either fully disclosed option does not require another
  approval.
- Clarified that workflow order, numeric values, retrieval timing, capture,
  graph, embeddings, and agent integration are adaptable guidance rather than
  required pipeline components.
- Made generated setup packs omit explicitly disabled components and allowed
  managed agent instructions to configure capture, recall, or both.
- Made fully vague setup requests ask one short source-and-outcome question
  before inspection, while contextual and detailed requests keep the fast path.
- Added read-only personalized project recommendations for questions such as
  `What can I do with Polygres?` without starting setup automatically.
- Added a direct reply that carries an accepted recommendation into setup
  without repeating discovery or bypassing the mutation review.

## 0.3.1 - 2026-08-11

### Changed

- Updated CLI guidance for one-call generated TSVector setup without a separate
  migration.
- Added text configuration get, update, diagnostics, reindex, limits, compound
  row-key, metadata, and filter guidance.
- Added text index and incomplete-cleanup troubleshooting steps using public,
  read-only evidence.
- Updated SDK guidance for compound result keys, SQL `NULL` filters, bound
  cursors, and the query-only text-search boundary.
- Updated retrieval design guidance for generated and existing TSVector modes,
  index ownership, limits, diagnostics, and deletion behavior.
- Raised the minimum supported CLI version to `0.2.1` for the expanded text
  configuration command surface.

## 0.3.0 - 2026-08-09

### Added

- Added pgContext guidance across the CLI, SDK, retrieval-design, and troubleshooting skills.
- Added workflows for setting up, querying, maintaining, and troubleshooting pgContext collections.
- Added guidance for choosing between pgContext, relational, graph, pgvector, text, and hybrid retrieval.

### Changed

- Expanded SDK guidance for building and operating pgContext integrations.
- Expanded troubleshooting guidance for common pgContext failures.
- Preferred Polygres AI Context collections for new semantic retrieval setup.
- Reframed pgvector guidance around compatibility and management of existing
  registrations.
- Directed new CLI and SDK workflows to the supported Context collection
  surface.
- Prevented temporary pgGraph test fixtures from enabling RLS unless the test
  explicitly targets RLS behavior.
- Required agents to verify both PostgreSQL RLS flags before reporting a
  pgGraph product failure, and classify RLS-induced failures as fixture/setup
  incompatibilities.
- Required live tests to verify CLI and SDK versions and import origins, and to
  reinstall both packages from the source checkout instead of PyPI when testing
  checkout code.

## 0.2.0 - 2026-07-14

### Added

- Added `polygres-retrieval-design` for comparing retrieval approaches and producing reviewable implementation plans without changing a project.
- Added `polygres-troubleshooting` for evidence-based diagnosis through public, read-only interfaces.
- Added installation and discovery metadata for Codex and Claude Code.

## 0.1.0 - 2026-07-10

### Added

- Initial Polygres Agent Skills distribution.
- Added `polygres-cli` for safe project operations, imports, migrations, Runtime API keys, and retrieval configuration.
- Added `polygres-sdk` for Python graph, vector, text, hybrid, and grounded RAG application workflows.
