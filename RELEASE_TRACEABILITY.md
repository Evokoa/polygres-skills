# Polygres Agent Skills release traceability

Date: 2026-09-13

Scope: update all five Agent Skills for Polygres embedding generation and
CLI/SDK `0.5.0`, preserving existing `0.4.x` vector workflows.

## Release identity

Canonical version: `0.7.0`

Release record: `releases/0.7.0.json`

The release record binds the plugin payload and standalone skill mirrors with
a deterministic digest. The skills package has its own version, independent
of the CLI and SDK releases.

## Implemented behavior

- Configure embedding generation through discovered MCP tools, CLI commands,
  or the Dashboard, using the live model catalog and preview before setup.
- Use the SDK's existing Context and hybrid query methods for text and vector
  queries. Embedding generation configuration stays outside the SDK.
- Resolve query models through the selected collection vector and its saved
  embedding configuration.
- Record separate generation and query allowances, monetary model pricing,
  project spending permission, and request-level credit opt-in.
- Support managed embedding output for synchronized text while keeping source
  row writes in the source PostgreSQL database.
- Keep local and external embedding workflows available, including existing
  vectors and clients that predate text query generation.
- Verify generation progress and Context collection/index readiness separately.
- Preserve idempotency keys and distinguish transient errors, funding issues,
  and provider outcomes that need reconciliation.
- Keep one canonical MCP reference and identical generated copies in all five
  skills, covering the current catalog's 102 tools.
- Correct the MCP configuration-update description to list the settings its
  public schema accepts, with batch sizing managed by Polygres.

## Acceptance mapping

| Acceptance criterion | Implementation | Verification |
| --- | --- | --- |
| CLI workflows use supported commands and arguments | CLI embedding and Context references | Parser and mocked request checks against CLI `0.5.0` |
| SDK examples use existing methods | SDK Context, hybrid, and client references | SDK signatures and recorded request payloads |
| Managed pipelines produce the correct setup pack | Pipeline recommendation, validation, rendering, and scaffolding scripts | Standard and synchronized managed-plan tests alongside local/external regression cases |
| Retrieval plans include model binding, usage, and readiness | Retrieval-design references and plan template | Per-skill source review and contract checks |
| Diagnostics select recovery from public evidence | Troubleshooting references | CLI/parser and public error-contract checks |
| Every MCP tool is documented | Canonical MCP tool contract | Coverage against the server policy catalog |
| Each installed skill is self-contained | Generated reference copies and exported mirrors | Full-content comparison, skill validation, and temporary export checks |
| Release metadata matches the shipped files | Version, manifests, release record | Release validation and payload digest |

## Release verification scope

Local verification uses source contracts, mocked requests, generated temporary
setup packs, and package exports. It does not require live project changes,
embedding provider calls, or spending credits. Installation channel results
are recorded separately from local validation in the release record.

## Local results

- Standard package suite: 181 passed.
- Cross-package suite in the MCP environment: 17 passed, with no skipped tests.
- CLI embedding and text-query source tests: 23 passed.
- MCP embedding and text-query source tests: 26 passed.
- Ruff, all five skill validators, Codex plugin validation, and Claude plugin
  and marketplace validation passed.
- Package and release validation passed for `polygres-skills-v0.7.0`.
- A temporary public export passed validation with 79 identical mirrored skill
  files and the same release digest.

## Publication checks

- Verify clean-machine installation from the published skills repository.
- Verify Codex plugin loading of the production MCP connection.
- Complete browser OAuth and installation consent against the deployed service.
- Verify fixed-project and organization-wide discovery with representative
  roles and feature selections.
