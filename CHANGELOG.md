# Changelog

All notable changes to Polygres Agent Skills are documented in this file.

## 0.3.0 - 2026-08-08

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
