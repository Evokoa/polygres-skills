# Polygres Agent Skills release traceability

Date: 2026-08-18

Scope: release synchronized PostgreSQL project guidance and executable safety
boundaries in Agent Skills `0.5.0`, coordinated with CLI `0.4.0` and SDK
`0.4.0`.

## Release identity

Canonical version: `0.5.0`

Release record: `releases/0.5.0.json`

The installable payload digest is recorded in the release record. Live Codex,
Claude Code, skills CLI, and clean-machine installation remain unverified
release gates.

## Implemented behavior

- Resolve standard versus synced project mode before selecting ingestion,
  database, CLI, SDK, or Runtime surfaces.
- Evaluate managed sync for eligible Supabase, Neon, or PostgreSQL sources when
  a new project is acceptable and the source remains authoritative.
- Route initial project creation and table selection through
  `polygres projects create sync` or the dashboard without collecting source
  credentials. Keep later reconfiguration and lifecycle work in the dashboard.
- Restrict synced Runtime guidance to graph, text, existing vector, hybrid,
  Context, retrieval readiness, and table catalog surfaces.
- Reject target schema changes, imports, rows, backfills, target database
  credentials, custom capture workers, and unsupported sync control in the
  deterministic plan validator while allowing CLI sync creation.
- Omit target schema and checkpoint artifacts from managed-sync scaffolds.
- Record project mode, source authority, selected tables, continuous egress,
  managed publication and slot ownership, reconfiguration behavior, and
  source-only writes in the setup review.
- Keep application writes, deletes, schema changes, and embedding generation in
  the source PostgreSQL database.
- Restrict synced Context design to existing synchronized source tables and
  columns, and require both foreign-key endpoints in the selection for graph
  traversal.
- Diagnose public sync preflight result codes, lifecycle states, table resync,
  generation conflicts, schema drift, storage pressure, and expected surface
  permission errors without mutation or secret collection.
- Preserve the adaptive standard-project pipeline workflow and its existing
  safety, approval, embedding, capture, and retrieval behavior.

## Acceptance mapping

| Acceptance criterion | Implementation | Verification |
| --- | --- | --- |
| Existing PostgreSQL sources route to managed sync when eligible. | Data-pipeline workflow and `synced-projects.md` | Source-routing text tests |
| Synced plans cannot target unsupported mutation surfaces. | `validate_pipeline_plan.py` | Synced blocker-family tests for ten unsupported paths |
| Managed-sync scaffolds omit custom ingestion artifacts. | `scaffold_pipeline.py` | Synced scaffold regression test |
| Reviews disclose sync authority and scope. | `render_pipeline_review.py` | Synced review assertions |
| CLI guidance matches typed standard and sync creation without exposing source credentials. | CLI project references | CLI creation and command-boundary tests |
| SDK guidance is Runtime-only and mode aware. | SDK synced reference and SDK 0.4.0 example | SDK synced-boundary test |
| Troubleshooting separates source, control plane, and Runtime. | Troubleshooting synced reference | Preflight and lifecycle coverage test |
| Retrieval designs remain valid after sync selection changes. | Retrieval design references | Synced retrieval-design test |
| Public project documentation matches reconfiguration behavior. | PostgreSQL sync guide | Package documentation review |
| Existing skill behavior remains coherent. | All five skills and package metadata | Full non-heavy package test suite |

No live Polygres project was mutated. No dependency was installed. No remote
repository, marketplace, commit, or deployment was changed by this work.

## Known limitations

- CLI `0.4.0` creates standard and synchronized projects but does not expose
  existing-sync reconfiguration, pause, resume, retry, resnapshot, or credential
  rotation commands.
- The Python SDK local `project_mode="synced"` guard requires SDK `0.4.0`.
- Synced-project creation, preflight, table selection, reconfiguration, and
  lifecycle work do not have first-class CLI or SDK workflows.
- Source credential rotation is not presented as a self-service workflow
  because the dashboard currently hides it.
- Clean-machine remote installation and live Codex or Claude activation remain
  external release gates.
