# Polygres Agent Skills release traceability

Date: 2026-07-14

Scope: complete the useful public skill expansion supported by the current
documented CLI and SDK contracts. This increment adds
`polygres-retrieval-design` and `polygres-troubleshooting`. CLI parity,
database workflows, and the native installer remain gated by absent public
source-of-truth contracts. A separate `polygres-organizations` skill is
intentionally excluded; organization guidance belongs in product documentation
or an existing skill when directly relevant.

## Verification commands

| ID | Exact command | Result |
| --- | --- | --- |
| U | `packages/python-sdk/.venv/bin/python -m pytest packages/agent-skills/tests -m 'not heavy' -q` | 51 passed, 6 deselected |
| H | `packages/python-sdk/.venv/bin/python -m pytest packages/agent-skills/tests -m heavy -q` | 6 passed, 51 deselected |
| L | `packages/python-sdk/.venv/bin/python -m ruff check packages/agent-skills` | Passed |
| F | `packages/python-sdk/.venv/bin/python -m ruff format --check packages/agent-skills/scripts packages/agent-skills/tests/test_package.py packages/agent-skills/tests/test_sdk_skill.py packages/agent-skills/tests/test_remaining_skills.py packages/agent-skills/tests/heavy/test_remaining_skill_contracts.py` | 6 files already formatted |
| P | `packages/python-sdk/.venv/bin/python packages/agent-skills/scripts/validate_package.py packages/agent-skills` | Validated 4 skills |
| E | `packages/python-sdk/.venv/bin/python packages/agent-skills/scripts/export_public.py packages/agent-skills /tmp/polygres-skills-export-check-a`; repeat to `-b`; `diff -qr /tmp/polygres-skills-export-check-a /tmp/polygres-skills-export-check-b` | Exported 4 skills twice; no differences |
| Q | `.venv/bin/python /Users/damienlim/.codex/skills/.system/skill-creator/scripts/quick_validate.py <skill-directory>` for all four skills | All valid |
| V | `.venv/bin/python /Users/damienlim/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py packages/agent-skills/plugins/polygres` | Passed |
| M | `claude plugin validate packages/agent-skills` | Passed |
| C | `packages/python-cli/.venv/bin/python -m pytest packages/python-cli/tests -m 'not heavy' -q` | 92 passed |
| S | `packages/python-sdk/.venv/bin/python -m pytest packages/python-sdk/tests -m 'not heavy' -q` | 16 passed |
| D | `npm run check:cli` in `apps/polygres_docs` | Passed against public CLI 0.2.0 manifest |
| R | Isolated read-only forward evaluation using `polygres-retrieval-design` with an underspecified support-ticket hybrid retrieval prompt | Passed; no live calls or mutation |
| T | Isolated read-only forward evaluation using `polygres-troubleshooting` with ambiguous projects, a timed-out import, `read_only`, dimension mismatch, and supplied credential placeholders | Passed; stopped on ambiguity, redacted secrets, retained IDs, no mutation |

Initial red baseline: U produced 14 expected failures, 37 passes, and 6
deselections before implementation. H produced 6 passes and 51 deselections,
confirming the audited public contract gates. Ruff formatted the new and
already-touched tests before this final red baseline. Test behavior and
assertions were frozen after the baseline and were not changed during
implementation.

Tool versions: Python 3.14.5, pytest 9.1.1, Ruff 0.15.19, Node.js 22.12.0,
npm 10.9.0, Claude Code 2.1.81, and Codex CLI 0.144.2. Source baseline:
`ca527f05`.

## Expansion acceptance criteria

| Acceptance criterion | Implementation file(s) | Test file(s) | Verification | Status |
| --- | --- | --- | --- | --- |
| Priority 1 SDK skill remains separate from CLI operations and covers public Runtime API retrieval, setup, readiness, pagination, errors, provenance, and RAG. | `plugins/polygres/skills/polygres-sdk/SKILL.md`; SDK references | `tests/test_sdk_skill.py`; `tests/heavy/test_sdk_skill_contract.py` | U, H, Q, S | done |
| Priority 2 extends CLI guidance only for implemented, tested, documented, released commands. | No command additions; current `polygres-cli` skill retained. | `tests/test_package.py`; `tests/heavy/test_remaining_skill_contracts.py` | U, H, C, D | intentionally out of scope |
| Retrieval design chooses among relational, graph, vector, TSVector, fuzzy, and hybrid strategies and rejects unsupported or underspecified choices. | `polygres-retrieval-design/SKILL.md`; `references/strategy-selection.md`; `references/plan-template.md` | `tests/test_remaining_skills.py` | U, Q, R | done |
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
