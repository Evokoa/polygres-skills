# Polygres Agent Skills

Agent Skills for operating managed Polygres projects, designing retrieval,
building Python applications, and diagnosing failures through public surfaces.

The plugin contains four independently triggered skills:

- `polygres-cli` for project operations, imports, migrations, keys, and
  retrieval configuration;
- `polygres-sdk` for graph, vector, text, hybrid, and grounded RAG application
  code;
- `polygres-retrieval-design` for reviewable relational, graph, vector, text,
  hybrid, and RAG plans without mutating a project;
- `polygres-troubleshooting` for read-only diagnosis using public CLI and SDK
  evidence.

Source repository:
[Evokoa/polygres-skills](https://github.com/Evokoa/polygres-skills)

## Install

Install with the cross-agent skills installer:

```bash
npx skills add Evokoa/polygres-skills
```

Install explicitly for Codex and Claude Code at user scope:

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

Open `/plugins`, choose the Polygres marketplace, and install Polygres. Start a
new task after installation.

### Claude Code plugin marketplace

Inside Claude Code:

```text
/plugin marketplace add Evokoa/polygres-skills
/plugin install polygres@polygres
/reload-plugins
```

Compatible agents can activate the appropriate skill automatically from the
request. Invoke a skill explicitly when you need to select the CLI or SDK
workflow yourself:

```text
/polygres:polygres-cli
/polygres:polygres-sdk
/polygres:polygres-retrieval-design
/polygres:polygres-troubleshooting
```

## Update

Update a generic Agent Skills installation:

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

Remove a global generic installation:

```bash
npx skills remove --global polygres-cli
npx skills remove --global polygres-sdk
npx skills remove --global polygres-retrieval-design
npx skills remove --global polygres-troubleshooting
```

For Codex, uninstall Polygres through `/plugins`, then optionally remove the
marketplace:

```bash
codex plugin marketplace remove polygres
```

For Claude Code:

```text
/plugin uninstall polygres@polygres
/plugin marketplace remove polygres
/reload-plugins
```

## Use

Describe the outcome you want. The agent selects the documented CLI workflow
and asks before destructive or secret-producing operations.

Example prompts:

```text
Log me into Polygres and help me select the correct project.
```

```text
Import customers.json into public.customers. Inspect it first, explain any
conversion choices, and ask before changing data.
```

```text
Review this SQL migration and ask before applying it to my selected Polygres
project.
```

```text
Configure vector retrieval for documents.embedding with 1536 dimensions and
verify readiness.
```

```text
Use the Polygres SDK to retrieve semantically similar documents, expand their
citations, and build a deduplicated context with provenance.
```

```text
Design a reviewable retrieval plan for this schema. Compare relational, graph,
vector, text, and hybrid strategies without changing the project.
```

```text
Diagnose why this import timed out. Preserve job and request IDs, use only
public read-only evidence, and recommend the safest next action.
```

## Retrieval design and troubleshooting

Use `polygres-retrieval-design` before configuration when the retrieval model
or strategy is unsettled. It records verified schema facts, unresolved
assumptions, graph and embedding choices, authorization, provenance,
deduplication, token budgets, validation, and separate CLI and SDK handoffs.

Use `polygres-troubleshooting` after a failure. It resolves identity and exact
project context, checks public readiness and job state, distinguishes local
CLI, control-plane, Runtime API, and Postgres failures, and retains request and
job IDs. It does not use private observability or perform repair mutations.

## Python SDK applications

Install `polygres-sdk` in the application environment separately from
`polygres-cli`. The SDK skill helps select the project Runtime API URL, load the
API key from server-side environment configuration, check readiness, and write
typed graph, vector, text, or hybrid retrieval code.

It preserves these boundaries:

- application retrieval uses the per-project Runtime API, not the central
  control-plane or Postgres URLs;
- graph calls use real row IDs returned from trusted application data or prior
  retrieval results;
- connection information is passwordless;
- filters narrow retrieval but do not replace application authorization;
- pagination, request IDs, provenance, deduplication, and context token budgets
  remain explicit.

## Data formats

The current Polygres CLI imports CSV. The skill can prepare TSV, JSON arrays,
and JSONL/NDJSON locally as CSV before invoking the supported import command.
The preparation workflow does not upload the original non-CSV file and does
not make network requests.

Excel, Parquet, Avro, ORC, XML, YAML, SQL dump, and custom `pg_dump` conversion
are outside the first release. Export those sources to CSV or JSONL first.

## Security

- Browser login is the public authentication flow.
- Database passwords are never retrieved or passed in command arguments.
- Runtime API-key secrets are shown once and can enter terminal or agent
  history. Run key creation directly when transcript exposure is unacceptable.
- Replacement imports, migrations, revocations, deletes, and schema mutations
  require explicit approval.
- The skill uses the public CLI and does not call private Polygres endpoints.

## Compatibility

Skill release `0.2.0` targets `polygres-cli >= 0.1.0` and `polygres-sdk >=
0.1.0`. Installed CLI help and the installed Python SDK signatures remain
authoritative when local package versions differ from examples.

## License

Apache License 2.0. See `LICENSE`.
