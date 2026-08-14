# Polygres Agent Skills release traceability

Date: 2026-08-14

Scope: release Context-aware single-row capture guidance in Agent Skills
`0.4.0`, coordinated with CLI and SDK `0.3.0` single-row writes.

## Release identity

Canonical version: `0.4.0`

Release record: `releases/0.4.0.json`

The installable payload digest is recorded in the release record. Live Codex,
Claude Code, and skills CLI installation remain unverified release gates.

## Implemented behavior

- Activates from broad intent such as `Help me set up Polygres`, contextual
  requests, or detailed technical specifications.
- For broad intent with neither a source nor an outcome, asks one direction
  question before inspection. Contextual and detailed requests proceed without
  that opening question.
- For capability questions, scans the accessible workspace and resolved
  Polygres project read-only, then recommends project-specific uses without
  starting setup or mutation. A direct reply carries an accepted recommendation
  into setup without repeating discovery or bypassing review.
- Inspects a bounded sample, infers reversible defaults, and asks one concise
  batch only for critical unknowns.
- Selects only useful components. Schema changes, embeddings, graph, backfill,
  continuous capture, retrieval code, and agent instructions are conditional.
- Treats workflow order and numeric values as adaptable defaults. Safety,
  authorization, embedding compatibility, public-interface support, graph
  evidence, approval, and truthful verification remain firm boundaries.
- Honors source-provided, local, hosted, or no-embedding choices. When local
  versus hosted is unknown, it silently ranks one compatible option from each
  allowed category using the bounded data sample and device report, then puts
  both inside the single setup review.
- Uses a versioned, source-cited model catalog and exact provider contracts.
  Selecting either fully disclosed embedding option counts as the one approval.
- Uses an internal permissive safety linter. Tiny plans are valid; warnings are
  handled silently. Only unresolved remote targets, secrets, stale material
  approvals, capability-proven unavailable interfaces, and unsupported
  operational claims block.
- Renders one concise mutation review. Approval remains valid while project,
  source scope, data egress, destructive effects, and paid processing remain
  unchanged.
- Adds capability-gated CLI and SDK `0.3.0` single-row validation, insert,
  upsert, and ignore guidance. Bulk work continues to use import.
- Adds an idempotent, reversible managed block for scoped capture, recall, or
  both. The active instruction file changes only after the consolidated review
  is approved, and instructions alone remain best-effort.
- Uses one explicit Context-backed row operation for source persistence and
  point reconciliation while keeping embeddings and pgGraph independent.
- Keeps generic tables row-only unless a Context collection is explicitly
  selected or resolved safely.
- Persists per-record, per-surface pending state before advancing a source
  cursor when Context reconciliation has not completed.
- Extends retrieval-design handoff and troubleshooting evidence so the setup
  flow can continue without repeating discovery or approval.

## Acceptance mapping

| Acceptance criterion | Implementation | Verification |
| --- | --- | --- |
| Short and detailed prompts activate setup. | Data-pipeline frontmatter and workflow; package README | Skill text tests |
| Fully vague prompts establish direction before inspection. | Vague-opening branch and guided question | Vague-prompt routing test |
| Capability questions receive project-specific recommendations. | Read-only recommendation branch | Personalized-recommendation routing test |
| Accepted recommendations transition directly into setup. | Recommendation call to action and context handoff | Recommendation-to-setup routing test |
| Optional components stay optional. | Permissive linter and conditional scaffolder | Minimal-plan scaffold test |
| Explicitly disabled components produce no files or review effects. | Conditional scaffolder, review, and approval boundary | Disabled-component regression test |
| Only material safety failures block. | `validate_pipeline_plan.py` | Five blocker families and warning-only plan tests |
| Approval survives harmless implementation changes. | Boundary-only approval digest | Approval digest regression test |
| Agent instructions preserve user text and support independent capture or recall. | `update_agent_instructions.py` | Idempotency, removal, and recall-only tests |
| CLI and SDK use public single-row writes when available. | CLI/SDK `rows.md` references | Command and method guidance tests |
| Hosted embeddings remain explicit and secret-free. | Embedding plan guidance and linter | Hosted choice and secret tests |
| Embedding selection does not create a second interview. | Model catalog, recommender, and review renderer | Local/hosted ranking and approval-boundary tests |
| Existing skills remain coherent. | CLI, SDK, design, and troubleshooting updates | Package test suites |

No live Polygres project was mutated. No dependency was installed. No remote
repository, marketplace, commit, or deployment was changed by this work.

## Known limitations

- Guaranteed chat capture requires a tested host hook, wrapper, application
  path, outbox, or worker.
- The rows surface requires compatible CLI or SDK `0.3.0` and target Runtime
  capability evidence. Older environments receive an explicit upgrade path.
- ONNX requires a model-specific tokenizer and pooling adapter.
- Device feasibility and catalog resource estimates are conservative selection
  policy, not a performance benchmark. The selected model still requires a
  bounded smoke test.
- Clean-machine remote installation and live Codex or Claude activation remain
  external release gates.
