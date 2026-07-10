# Polygres Agent Skills

Agent Skills for operating managed Polygres projects through the public
`polygres` command-line interface.

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
  --skill polygres-cli \
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

Invoke the bundled skill explicitly with:

```text
/polygres:polygres-cli
```

## Update

Update a generic Agent Skills installation:

```bash
npx skills update polygres-cli
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

Skill release `0.1.0` targets `polygres-cli >= 0.1.0`. The installed
`polygres --help` output remains authoritative when command surfaces differ.

## License

Apache License 2.0. See `LICENSE`.
