# Polygres Agent Skills

Polygres Agent Skills help coding agents set up data pipelines, operate projects,
design retrieval, write applications, and diagnose failures using supported
Polygres interfaces.

User guide: [Polygres Agent Skills](https://docs.polygres.com/agent-skills)

## Choose a skill

| Skill | Use it for |
| --- | --- |
| `polygres-data-pipeline` | Set up the smallest useful Polygres ingestion, retrieval, memory, or agent integration from a short or detailed request. |
| `polygres-cli` | Sign in, select projects, write one row, import data, apply migrations, manage Runtime API keys, and configure retrieval. |
| `polygres-sdk` | Write application rows and build Python retrieval with Polygres AI Context, graph, text, hybrid, or existing vectors. |
| `polygres-retrieval-design` | Compare retrieval approaches and produce an implementation plan without changing a project. |
| `polygres-troubleshooting` | Diagnose CLI, API, PostgreSQL, job, migration, and retrieval failures using read-only evidence. |

Compatible agents select the appropriate skill automatically. You can also name the skill in your request when you want a specific workflow.

## Install

### Agent Skills installer

```bash
npx skills add Evokoa/polygres-skills
```

To install globally for Codex and Claude Code:

```bash
npx skills add Evokoa/polygres-skills \
  --global \
  --agent codex \
  --agent claude-code \
  --yes
```

### Codex plugin marketplace

```bash
codex plugin marketplace add Evokoa/polygres-skills
codex
```

Open `/plugins`, choose the Polygres marketplace, install Polygres, and start a new task.

### Claude Code plugin marketplace

Run these commands inside Claude Code:

```text
/plugin marketplace add Evokoa/polygres-skills
/plugin install polygres@polygres
/reload-plugins
```

## Try it

Ask for the outcome you want in one short line or a detailed specification. The
skill infers the workflow from intent, inspects relevant state, and asks only
for critical information it cannot safely discover.

```text
Help me set up Polygres.
```

```text
What can I do with Polygres?
```

```text
Look at my data and use $polygres-data-pipeline to set up a Polygres data pipeline.
```

For a request that names a source or outcome, the pipeline skill takes a
bounded sample, applies safe defaults, selects only useful components, and
creates runnable source-specific code. For a fully vague request such as `Help
me set up Polygres`, it first asks one short question about the desired outcome
and relevant data, then begins inspection. Schema changes, embeddings, graph,
backfill, continuous capture, retrieval, and agent instructions are optional.
Sample sizes, retrieval timing,
and numeric limits are starting defaults that adapt to the user's setup. Before
remote mutation or changing active agent instructions, it shows one concise
review and asks once. Internal lint warnings do not become user questions.

For `What can I do with Polygres?`, the skill performs a bounded, read-only
scan of the accessible workspace and current Polygres project, then recommends
the most useful next step for that specific project. It does not change or
scaffold anything until the user chooses a recommendation. The response ends
with a direct setup reply, such as `Set up the recommended Polygres pipeline`.
That reply carries the recommendation into the setup flow without repeating
discovery; the skill still shows the consolidated review before changes.

The same adaptive flow works with prompts such as:

```text
Look at my conversations and set up a Polygres data pipeline.
```

```text
Look at my current setup and set up a Polygres data pipeline.
```

```text
Log me into Polygres and help me select the correct project.
```

```text
Import customers.json into public.customers. Inspect it first and explain any
conversion choices before changing data.
```

```text
Configure Polygres AI Context retrieval for documents.embedding with 1536
dimensions and verify readiness.
```

```text
Use the Polygres SDK to retrieve similar documents, expand their citations,
and build deduplicated context with source references.
```

```text
Design a retrieval plan for this schema. Compare relational, graph, text,
hybrid, Polygres AI Context, and any existing vector configuration without
changing the project.
```

```text
Diagnose why this pgContext collection is blocked. Use read-only evidence and
recommend the safest next action.
```

## What the skills protect

The skills follow a few important boundaries:

- They use public Polygres CLI, Runtime API, SDK, and PostgreSQL interfaces.
- The pipeline skill records separate documented store and retrieve interfaces,
  selecting CLI, SDK, or Runtime API based on the workload. SDK and CLI 0.3.0
  provide capability-gated single-row validation, insert, upsert, and ignore.
  Direct Postgres remains an explicitly approved compatibility fallback.
- They ask before imports, migrations, revocations, deletions, and schema changes.
- They keep database passwords out of command arguments and generated code.
- They treat Runtime API keys as secrets and warn when a command can expose one in terminal or agent history.
- They keep authorization in the application. Retrieval filters can narrow results, but they do not replace access control.
- They preserve request IDs and relevant resource IDs when diagnosing a failure.
- They honor a known embedding preference. If local versus hosted is unknown,
  they silently inspect compatibility and include one local recommendation and
  one hosted alternative in the single setup review. Selecting either reviewed
  option is the one approval. Polygres does not generate embeddings.
- They generate `.env.example`, ensure `.env` is ignored, and tell the user how
  to paste credential values into `.env` without exposing them to the agent.

## Import formats

The Polygres CLI imports CSV directly. The CLI skill can safely prepare TSV, JSON arrays, and JSONL or NDJSON as CSV before starting an import. It does not upload the original source file.

Export Excel, Parquet, Avro, ORC, XML, YAML, SQL dump, and custom `pg_dump` sources to CSV or JSONL before using this workflow.

## Update

Update an Agent Skills installation:

```bash
npx skills update polygres-data-pipeline
npx skills update polygres-cli
npx skills update polygres-sdk
npx skills update polygres-retrieval-design
npx skills update polygres-troubleshooting
```

Refresh the Codex marketplace:

```bash
codex plugin marketplace upgrade polygres
```

Then open `/plugins` to update or reinstall Polygres if prompted.

For Claude Code:

```text
/plugin marketplace update polygres
/plugin update polygres@polygres
/reload-plugins
```

## Uninstall

Remove a global Agent Skills installation:

```bash
npx skills remove --global polygres-data-pipeline
npx skills remove --global polygres-cli
npx skills remove --global polygres-sdk
npx skills remove --global polygres-retrieval-design
npx skills remove --global polygres-troubleshooting
```

For Codex, uninstall Polygres through `/plugins`, then optionally remove the marketplace:

```bash
codex plugin marketplace remove polygres
```

For Claude Code:

```text
/plugin uninstall polygres@polygres
/plugin marketplace remove polygres
/reload-plugins
```

## Compatibility

Package version: [`0.4.0`](https://github.com/Evokoa/polygres-skills/releases/tag/polygres-skills-v0.4.0). It is coordinated with `polygres-cli 0.3.0` and `polygres-sdk 0.3.0`. If an example differs from your installed version, follow the installed CLI help or SDK method signature.

## Changelog

See the [Agent Skills 0.4.0 release notes](https://github.com/Evokoa/polygres-skills/releases/tag/polygres-skills-v0.4.0) for release changes.

## License

Apache License 2.0. See `LICENSE`.
