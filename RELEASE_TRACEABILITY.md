# Polygres Agent Skills release traceability

Date: 2026-09-05

Scope: connect Agent Skills `0.6.0` to Polygres MCP catalog `1.0` while
preserving the existing CLI `0.4.x` and SDK `0.4.x` workflows.

## Release identity

Canonical version: `0.6.0`

Release record: `releases/0.6.0.json`

The release payload records a deterministic digest. Live marketplace and OAuth
qualification remain release gates until the deployed MCP service and public
skills package are available together.

## Implemented behavior

- Interpret MCP vector and hybrid readiness as legacy compatibility evidence,
  not Context readiness or a recommendation to configure a retired surface.
- Require Context capabilities, collections, status, verification, and
  named-vector index evidence before reporting semantic retrieval unavailable.
- Install the production Streamable HTTP MCP connection with the Codex plugin.
- Start MCP-aware work from discovery, `whoami`, connection targeting, project
  mode, and current project state.
- Prefer discovered compatible MCP tools for interactive work.
- Preserve CLI, SDK, Dashboard, source PostgreSQL, and legacy retrieval
  workflows for operations outside the MCP catalog.
- Use one canonical MCP contract and generated hash-bound copies in all five
  skills.
- Cover all 91 catalog tools and the eight feature groups.
- Preserve action-bound confirmation, idempotency keys, operation IDs, request
  IDs, provenance, and bounded result handling.
- Route synchronized source credentials and Dashboard-started imports through
  their secure browser workflows.
- Add focused playbooks for the eight launch outcomes.

## Acceptance mapping

| Acceptance criterion | Implementation | Verification |
| --- | --- | --- |
| Codex loads Polygres MCP with the skills | `.codex-plugin/plugin.json` and `.mcp.json` | Manifest and package validation |
| Skills understand every launch tool | Canonical MCP tool contract | Server-policy catalog coverage test |
| Installed skills remain self-contained | Generated contract copies | SHA-256 copy validation |
| Fixed and multi-project calls stay distinct | Shared contract and all skill entrypoints | Routing tests |
| Mutations use user approval and server confirmation | Shared contract and focused playbooks | Confirmation behavior assertions |
| Existing operational surfaces remain available | CLI, SDK, Dashboard, and pipeline fallbacks | Full skill regression suite |
| Public docs support MCP users | MCP connection, capability, action, and workflow pages | Public docs checks and build |

No live Polygres project was mutated. No dependency was installed. No remote
repository, marketplace, commit, or deployment was changed by this work.

## Release gates

- Verify clean-machine installation from the public skills repository.
- Verify Codex plugin loading of `.mcp.json`.
- Complete browser OAuth against the deployed production MCP endpoint.
- Exercise fixed-project and organization-wide discovery with representative
  roles and feature selections.
