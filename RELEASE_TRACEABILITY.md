# Polygres Agent Skills release traceability

Date: 2026-08-09

Scope: extend the four role-based public skills with pgContext guidance backed by the released CLI and SDK contracts. Release `0.3.0` keeps operations, application development, retrieval design, and troubleshooting separate while covering one coherent Context lifecycle. It also prevents temporary pgGraph fixtures from enabling RLS unless RLS behavior is the explicit test target, and requires live tests to verify current CLI and SDK versions and source origins. Broader database workflows and the native skill installer remain gated by absent public source-of-truth contracts. A separate `polygres-organizations` skill remains intentionally excluded; organization guidance belongs in product documentation or an existing skill when directly relevant.

## Release identity

Release `0.3.0` uses `VERSION` as its canonical version and validates matching Codex, Claude, marketplace, release-record, and `polygres-skills-vX.Y.Z` tag values. The structured record is `releases/0.3.0.json`. Its deterministic installable-payload digest is `sha256:43440721416a44d118f614cb5e6311b27d0e8002050d82fadfdac33dafa22cf8`.

The release record identifies CLI `0.2.0` as the minimum supported version and CLI `0.2.1` as the maximum tested version. SDK `0.2.0` is both the minimum supported and maximum tested version. The skills CLI installation channel remains explicitly unverified rather than claiming an unknown tool version.

## pgContext guidance expansion

Release `0.3.0` adds pgContext AI Search to every applicable role-based skill without adding an overlapping feature-specific skill:

- `polygres-retrieval-design` prefers pgContext collections for new semantic retrieval, distinguishes them from existing pgvector configurations, and plans embeddings, ownership, synchronization, retrieval modes, migration, and preview compatibility;
- `polygres-cli` guides capability discovery, source discovery, preflight, approval-gated creation, filters, point synchronization, retrieval, durable operations, diagnostics, and deletion;
- `polygres-sdk` covers Context capabilities, automated collection setup, point mutation union responses, every retrieval mode, trusted authorization filters, typed results, recovery-safe idempotency, and compatibility reads through existing vector configurations;
- `polygres-troubleshooting` diagnoses Context capability, collection, index, point, operation, recall, text, graph, Joint, admission, and timeout failures from public read-only evidence.

Verification for this increment:

| Check | Result |
| --- | --- |
| Non-heavy package tests | 73 passed, 7 deselected |
| Heavy CLI and SDK source-contract tests | 7 passed, 73 deselected |
| Package validator | Validated 4 skills |
| Release contract | Version, manifests, release record, digest, and proposed `polygres-skills-v0.3.0` tag value matched |
| Release-record schema | Valid against `releases/schema.json` |
| Skill Creator quick validation | All 4 skills valid |
| Ruff lint and touched-test format check | Passed |
| CLI documentation verifier | Passed |
| Deterministic public export | Exported twice with no differences |

No live Polygres project was mutated while validating the skill update.

## Verification commands

| ID | Exact command | Result |
| --- | --- | --- |
| U | `.venv/bin/python -m pytest packages/agent-skills/tests -m 'not heavy' -q` | 73 passed, 7 deselected |
| H | `.venv/bin/python -m pytest packages/agent-skills/tests -m heavy -q` | 7 passed, 73 deselected |
| L | `.venv/bin/python -m ruff check packages/agent-skills` | Passed |
| P | `.venv/bin/python packages/agent-skills/scripts/validate_package.py packages/agent-skills` | Validated 4 skills |
| X | `.venv/bin/python packages/agent-skills/scripts/release_version.py check --tag polygres-skills-v0.3.0` | Version, manifests, release record, digest, and proposed tag value matched; no public tag was created |
| E | `.venv/bin/python packages/agent-skills/scripts/export_public.py packages/agent-skills <temporary-directory>` | Exported 4 skills |
| Q | `.venv/bin/python /Users/damienlim/.codex/skills/.system/skill-creator/scripts/quick_validate.py <skill-directory>` for all four skills | All valid |
| V | `.venv/bin/python /Users/damienlim/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py packages/agent-skills/plugins/polygres` | Passed |
| M | `claude plugin validate packages/agent-skills` | Passed |
| C | `.venv/bin/python -m pytest packages/python-cli/tests -q` | 324 passed, 1 skipped |
| S | `.venv/bin/python -m pytest packages/python-sdk/tests -q` | 87 passed |
| D | `npm run check:cli` in `apps/polygres_docs` | Passed against the CLI 0.2.1 source manifest |
| R | Isolated read-only forward evaluation using `polygres-retrieval-design` with an underspecified support-ticket hybrid retrieval prompt | Passed; no live calls or mutation |
| T | Isolated read-only forward evaluation using `polygres-troubleshooting` with ambiguous projects, a timed-out import, `read_only`, dimension mismatch, and supplied credential placeholders | Passed; stopped on ambiguity, redacted secrets, retained IDs, no mutation |

Initial red baseline: U produced 14 expected failures, 37 passes, and 6 deselections before implementation. H produced 6 passes and 51 deselections, confirming the audited public contract gates. Ruff formatted the new and already-touched tests before this final red baseline. Test behavior and assertions were frozen after the baseline and were not changed during implementation.

Version-contract verification used Python 3.14.6, pytest 9.1.1, and Ruff 0.15.22. The behavioral evaluations used Claude Code 2.1.81 and Codex CLI 0.144.2. Source baseline: `ca527f05`.

## Expansion acceptance criteria

| Acceptance criterion | Implementation file(s) | Test file(s) | Verification | Status |
| --- | --- | --- | --- | --- |
| Priority 1 SDK skill remains separate from CLI operations and covers public Runtime API retrieval, pgContext lifecycle and durable operations, setup, readiness, pagination, errors, provenance, and RAG. | `plugins/polygres/skills/polygres-sdk/SKILL.md`; SDK references | `tests/test_sdk_skill.py`; `tests/heavy/test_sdk_skill_contract.py` | U, H, Q, S | done |
| Priority 2 CLI guidance covers implemented, tested, documented, and released pgContext commands without inventing unsupported flags or legacy configuration IDs. | `polygres-cli/SKILL.md`; `references/context.md` | `tests/test_package.py`; `tests/heavy/test_remaining_skill_contracts.py` | U, H, C, D | done |
| Retrieval design chooses among relational, graph, pgvector, TSVector, fuzzy, hybrid, and pgContext strategies and rejects unsupported or underspecified choices. | `polygres-retrieval-design/SKILL.md`; `references/strategy-selection.md`; `references/context-design.md`; `references/plan-template.md` | `tests/test_remaining_skills.py` | U, Q, R | done |
| Retrieval design covers nodes, stable row IDs, relationships, direction, bounded depth, fan-out, cycles, and graph provenance without invented identifiers. | `polygres-retrieval-design/references/graph-modeling.md` | `tests/test_remaining_skills.py` | U, Q, R | done |
| Retrieval design covers embedding model and dimensions, vector properties and filters, TSVector configuration, fuzzy fields, malformed input, empty input, and reindex policy. | `polygres-retrieval-design/references/vector-and-text-design.md` | `tests/test_remaining_skills.py` | U, Q, R | done |
| Retrieval design covers hybrid stage order, readiness, rebuild, authorization, provenance, deduplication, partial failure, and token budgets. | `polygres-retrieval-design/references/hybrid-and-rag-plan.md` | `tests/test_remaining_skills.py` | U, Q, R | done |
| Retrieval design produces a reviewable plan and never mutates directly; approved setup routes to `polygres-cli` and application code to `polygres-sdk`. | `polygres-retrieval-design/SKILL.md`; `references/plan-template.md` | `tests/test_remaining_skills.py` | U, Q, R | done |
| Troubleshooting resolves identity and exact project context, preserves request, job, and cursor IDs, and returns the required evidence-based diagnostic report. | `polygres-troubleshooting/SKILL.md`; `references/context-and-connectivity.md` | `tests/test_remaining_skills.py` | U, Q, T | done |
| Troubleshooting collects public readiness, project, database, import, migration, graph, vector, text, pagination, and SDK exception evidence. | `polygres-troubleshooting/references/projects-and-database.md`; `jobs-and-migrations.md`; `retrieval.md` | `tests/test_remaining_skills.py`; `tests/heavy/test_remaining_skill_contracts.py` | U, H, Q, C, S, T | done |
| Troubleshooting distinguishes local CLI, control-plane, Runtime API, Postgres or pooler, and asynchronous job failures; it covers timeouts, partial failures, rate limits, and compatibility mismatches. | `polygres-troubleshooting/references/errors-and-escalation.md`; `projects-and-database.md`; `jobs-and-migrations.md` | `tests/test_remaining_skills.py` | U, Q, T | done |
| Troubleshooting uses read-only checks first, avoids private endpoints and observability, never logs secrets, checks status before retry, and recommends approval-gated corrections. | `polygres-troubleshooting/SKILL.md`; all troubleshooting references | `tests/test_remaining_skills.py` | U, Q, T | done |
| Database workflows ship only after a supported public execution boundary exists. | No skill packaged; broader SQL automation remains excluded by `docs/51-user-cli-development-spec.md`. | `tests/test_remaining_skills.py`; `tests/heavy/test_remaining_skill_contracts.py` | U, H, C, D | intentionally out of scope |
| Native `polygres skills install/status/uninstall` ships only after its CLI source-of-truth contract is finalized. | No native installer implemented. | `tests/heavy/test_remaining_skill_contracts.py` | H, C, D | intentionally out of scope |
| Organization guidance does not become a separate skill without distinct public functionality. | `docs/56-polygres-agent-skill-release-spec.md`; no packaged skill | `tests/test_remaining_skills.py` | U, P, E | intentionally out of scope |
| Every new skill has distinct triggering, concise `SKILL.md`, focused references, OpenAI metadata, package documentation, compatible manifests, and deterministic export. | Both new skill directories; `README.md`; `apps/polygres_docs/src/content/agent-skills.mdx`; Codex and Claude manifests | `tests/test_remaining_skills.py`; `tests/test_sdk_skill.py` | U, P, E, Q, V, M, D | done |

## Distribution, safety, and definition of done

| Acceptance criterion | Implementation file(s) | Test file(s) | Verification | Status |
| --- | --- | --- | --- | --- |
| CLI examples map to the public parser and raw control-plane HTTP is not recommended. | `polygres-cli/SKILL.md`; CLI references; troubleshooting references | `tests/test_package.py`; `tests/heavy/test_remaining_skill_contracts.py` | U, H, C, D | done |
| JSON and JSONL import preparation, malformed metadata, escaping paths, missing resources, and unsupported formats remain covered. | `polygres-cli/references/data-imports.md`; `scripts/prepare_import.py`; public docs | `tests/test_prepare_import.py`; `tests/test_package.py`; `tests/test_sdk_skill.py` | U | done |
| Codex plugin, Claude marketplace, skill metadata, prompts, versions, and four-skill discovery validate. | Codex and Claude manifests; both `agents/openai.yaml` files | `tests/test_package.py`; `tests/test_remaining_skills.py`; `tests/test_sdk_skill.py` | U, P, Q, V, M | done |
| Public docs cover installation, automatic and explicit activation, first prompts, updates, removal, formats, security, retrieval design, and troubleshooting. | `README.md`; `apps/polygres_docs/src/content/agent-skills.mdx` | `tests/test_remaining_skills.py`; package tests | U, D | done |
| Public export is deterministic and includes one discovery mirror for every skill. | `scripts/export_public.py`; `.github/workflows/sync-agent-skills-repo.yml` | `tests/test_sdk_skill.py` | U, E | done |
| The remote public repository matches the monorepo export. | Sync workflow only; remote repository was not inspected or mutated. | No local test can prove remote state. | External check not run. | not done |
| A clean machine can install from the remote public repository. | Installation docs and manifests | No clean-machine external integration test. | External check not run. | not done |
| Plugin listing has an approved icon and has been visually reviewed in both marketplaces. | Manifests have name, publisher, descriptions, and prompts; no approved icon exists. | Manifest tests only | External marketplace review not run. | not done |
| Automatic activation selects every skill for representative and fuzzy prompts. | Distinct skill descriptions and metadata | Static ambiguity checks; isolated tests invoked the skill explicitly. | U, R, T; automatic activation not tested. | not done |
| Supported read-only and mutating workflows stop for consent and retain identifiers in both Codex and Claude. | Skill safety rules and references | Static package tests and read-only forward tests only | U, R, T; live disposable-project matrix not run. | not done |
| Database passwords and API keys are not exposed or bypassed in live-agent workflows. | All skill boundaries and secret-handling references | Static secret tests; troubleshooting secret-bearing forward test | U, T; live credential workflow not run. | not done |
| Timeout and partial-failure workflows retain project, migration, request, job, and cursor identifiers. | CLI automation/import/migration references; SDK error reference; troubleshooting references | Static tests and troubleshooting forward test | U, T; live asynchronous workflow not run. | not done |
| No placeholders, stale unsupported claims, em dashes, secrets, or unrelated generated artifacts remain in the task diff. | Entire task diff | Package scan and final diff review | U, L, `git diff --check`, targeted `rg`, and `git status --short` | done |
