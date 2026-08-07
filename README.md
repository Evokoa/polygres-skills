# Polygres Agent Skills

Polygres Agent Skills help coding agents operate projects, design retrieval, write Python applications, and diagnose failures using supported Polygres interfaces.

User guide: [Polygres Agent Skills](https://docs.polygres.com/agent-skills)

## Choose a skill

| Skill | Use it for |
| --- | --- |
| `polygres-cli` | Sign in, select projects, import data, apply migrations, manage Runtime API keys, and configure retrieval. |
| `polygres-sdk` | Build Python applications with pgContext, graph, vector, text, and hybrid retrieval. |
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

Ask for the outcome you want. The skill will inspect the relevant state and ask before destructive operations or actions that reveal secrets.

```text
Log me into Polygres and help me select the correct project.
```

```text
Import customers.json into public.customers. Inspect it first and explain any
conversion choices before changing data.
```

```text
Configure vector retrieval for documents.embedding with 1536 dimensions and
verify readiness.
```

```text
Set up a pgContext collection over public.documents. Preflight it first and
explain any schema changes before creating it.
```

```text
Use the Polygres SDK to retrieve similar documents, expand their citations,
and build deduplicated context with source references.
```

```text
Design a retrieval plan for this schema. Compare relational, graph, vector,
text, hybrid, and pgContext options without changing the project.
```

```text
Diagnose why this pgContext collection is blocked. Use read-only evidence and
recommend the safest next action.
```

## What the skills protect

The skills follow a few important boundaries:

- They use public Polygres CLI, Runtime API, SDK, and PostgreSQL interfaces.
- They ask before imports, migrations, revocations, deletions, and schema changes.
- They keep database passwords out of command arguments and generated code.
- They treat Runtime API keys as secrets and warn when a command can expose one in terminal or agent history.
- They keep authorization in the application. Retrieval filters can narrow results, but they do not replace access control.
- They preserve request IDs and relevant resource IDs when diagnosing a failure.

## Import formats

The Polygres CLI imports CSV directly. The CLI skill can safely prepare TSV, JSON arrays, and JSONL or NDJSON as CSV before starting an import. It does not upload the original source file.

Export Excel, Parquet, Avro, ORC, XML, YAML, SQL dump, and custom `pg_dump` sources to CSV or JSONL before using this workflow.

## Update

Update an Agent Skills installation:

```bash
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

Skill release `0.3.0` targets `polygres-cli >= 0.2.0` and `polygres-sdk >= 0.2.0`. If an example differs from your installed version, follow the installed CLI help or SDK method signature.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for release notes.

## License

Apache License 2.0. See `LICENSE`.
