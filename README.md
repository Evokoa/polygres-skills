# Polygres Agent Skills

Polygres Agent Skills help coding agents set up data pipelines, operate projects,
design retrieval, build applications, and diagnose failures. Install the Advisor
to load current guidance from [skills.polygres.com](https://skills.polygres.com/index.md),
or install the full skills package for local guidance and tools.

User guide: [Polygres Agent Skills](https://docs.polygres.com/agent-skills)

## Install

Both options install from this GitHub repository.

| Option | What you get | Choose it when |
| --- | --- | --- |
| Advisor only (recommended) | One lightweight skill that fetches relevant hosted guidance. | Your agent has web access and you want current guidance without installing all five skills. |
| Full skills package | Five local skills, helper scripts, and templates. Plugin marketplace installation also configures the Polygres MCP connection. | You want local guidance and execution resources. |

### Advisor only (recommended)

Install one skill that finds and loads the guidance relevant to your task:

```bash
npx skills add Evokoa/polygres-skills/meta/polygres-advisor
```

The Advisor reads the current hosted catalog and follows the skill and reference
links relevant to your task. It fetches guidance each session, so published
content updates do not require reinstalling the Advisor. It requires web access. It does not install an MCP
connection, CLI, SDK, helper scripts, or templates; execution uses the tools you
already have configured. If the website is unavailable, it can fall back to
compatible installed guidance when present.

### Without installation: pass the URL

Give a web-capable agent the [catalog URL](https://skills.polygres.com/index.md)
with your request:

```text
Use https://skills.polygres.com/index.md to help me choose a retrieval approach.
```

Include the URL each time you want the agent to consult the hosted guidance.

### Full skills package

Install all five skills locally when you want guidance available without fetching
the website, along with the helper scripts and templates used in execution.
Polygres operations still require the appropriate tools and service connection.

Use the Agent Skills installer:

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

This installs the skills and their resources. To include the Polygres MCP
connection, use your agent's plugin marketplace instead.

#### Codex

```bash
codex plugin marketplace add Evokoa/polygres-skills
codex
```

Open `/plugins`, choose the Polygres marketplace, install Polygres, and start a new task.

The Codex plugin installs the production Polygres MCP connection and all five
skills. Its base connection covers all accessible projects. Use the Polygres
Dashboard's project **Connect → MCP** page when you want a fixed-project
connection.

#### Claude Code

Run these commands inside Claude Code:

```text
/plugin marketplace add Evokoa/polygres-skills
/plugin install polygres@polygres
/reload-plugins
```

## Choose a skill

| Skill | Use it for |
| --- | --- |
| `polygres-data-pipeline` | Set up ingestion, PostgreSQL sync, embedding generation, retrieval, memory, and agent integration. |
| `polygres-cli` | Operate projects and configure embeddings and retrieval through MCP and the CLI. |
| `polygres-sdk` | Build Python integrations with existing vector inputs or text queries that Polygres embeds. |
| `polygres-retrieval-design` | Inspect project evidence and plan retrieval, embedding models, readiness, and usage. |
| `polygres-troubleshooting` | Diagnose connection, generation, indexing, quota, and retrieval issues using read-only evidence. |

These five skills are included in the full package and are also available as
hosted guidance through the Advisor. Compatible agents can select an installed
skill automatically, or you can name it in your request. Repository activation
restrictions continue to apply.

## Try it

With the Advisor, ask for guidance on the task you are working on:

```text
Use $polygres-advisor to help me choose a retrieval approach for my application.
```

For operational requests, configure a Polygres MCP connection or the appropriate
CLI/SDK first. The skills infer the workflow from your request, inspect relevant
state through available tools, and ask for critical information they cannot
safely discover.

```text
Use Polygres MCP to inspect this project and recommend the next useful setup step.
```

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
Sample sizes, retrieval timing, and numeric limits are starting defaults that adapt to the user's setup. It
prepares a concise review of remote changes and active agent instructions,
uses existing authorization, and asks when an additional choice or approval
is needed. Internal lint warnings do not become user questions.

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
Sync my Supabase, Neon, or PostgreSQL database into Polygres.
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
Generate embeddings for my articles and keep them up to date as the text changes.
```

```text
Update my existing SDK search to accept text and use the model configured for
my collection.
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

## How the skills work

The skills follow a few important boundaries:

- They use public Polygres CLI, Runtime API, SDK, and PostgreSQL interfaces.
- They resolve project mode before choosing a surface. Synced projects keep
  source writes in PostgreSQL and can use Polygres embedding generation for
  synchronized text.
- They use available MCP tools, CLI commands, or the dashboard for synchronized
  project setup and lifecycle work. Source credentials stay in the secure
  connection flow.
- The pipeline skill records separate documented store and retrieve interfaces,
  selecting CLI, SDK, or Runtime API based on the workload. CLI and SDK provide
  capability-gated single-row validation, insert, upsert, and ignore.
  On standard projects, direct Postgres remains an explicitly approved
  compatibility fallback.
- They prepare reviewable changes and use the authorization you have already
  given, asking when an additional choice or approval is needed.
- They keep database passwords out of command arguments and generated code.
- They treat Runtime API keys as secrets and warn when a command can expose one in terminal or agent history.
- They keep authorization in the application. Retrieval filters can narrow results, but they do not replace access control.
- They preserve request IDs and relevant resource IDs when diagnosing a failure.
- They honor your embedding preference and existing vectors. For Polygres
  generation, they inspect the available models and preview usage before setup.
  Local and external providers remain available when they fit your workflow.
- They configure generation through MCP, CLI, or the dashboard. Python
  applications use the SDK's existing Context and hybrid methods to search
  with text or vectors. Text queries use the selected collection vector's
  configured model and dimensions.
- They distinguish generation allowance from query allowance and show when
  additional credits need your project spending permission and opt-in.
- They generate `.env.example`, ensure `.env` is ignored, and tell the user how
  to paste credential values into `.env` without exposing them to the agent.

## Import formats

The Polygres CLI imports CSV directly. The CLI skill can safely prepare TSV, JSON arrays, and JSONL or NDJSON as CSV before starting an import. It does not upload the original source file.

Export Excel, Parquet, Avro, ORC, XML, YAML, SQL dump, and custom `pg_dump` sources to CSV or JSONL before using this workflow.

## Update

The Advisor fetches current hosted guidance in new sessions without needing to
be reinstalled. Update its installed instructions when the Advisor itself changes:

```bash
npx skills update polygres-advisor
```

Update the full package installed through the Agent Skills installer:

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

Remove an Advisor installed in the current project:

```bash
npx skills remove polygres-advisor
```

Add `--global` if you installed it globally.

Remove a global full-skills installation:

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

Package version: `0.9.0`. It supports Polygres MCP catalog `1.0`,
`polygres-cli 0.4.0` through `0.6.0`, and `polygres-sdk 0.4.0` through `0.5.0`.
Embedding setup and text query examples use CLI/SDK `0.5.0` and a service that
advertises the corresponding tools and capabilities. Existing vector workflows
remain available on `0.4.x`. Follow discovered MCP tools, installed CLI help,
and SDK method signatures for the version in use.

The Advisor and hosted library are introduced in `0.9.0`; they become available
when this release is published and the website is online.

## Changelog

Version `0.9.0` adds the optional Advisor and a hosted library of current skills
and references. The full package retains its local skills and resources.

Version `0.8.0` adds automatic chunking, targeted oversized recovery, and
readiness monitoring guidance for CLI `0.6.0`. Older command workflows remain
supported. These new features require a compatible server.

Version `0.7.0` added embedding generation workflows, text queries through the
existing SDK methods, and model, usage, and readiness guidance across all five
skills. See the [changelog](CHANGELOG.md) for the full release history.

## License

Apache License 2.0. See [LICENSE](LICENSE).
