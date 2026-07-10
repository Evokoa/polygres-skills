# Contributing

The canonical source for this package is `packages/agent-skills` in the private
Polygres monorepo. The public repository is generated from that directory, with
a deterministic `skills/polygres-cli` discovery mirror added during export. Do
not maintain a separate hand-edited public copy.

## Change a skill

1. Keep the core `SKILL.md` concise and move detailed workflows into focused
   references.
2. Verify every documented command against the current `polygres` CLI parser
   and installed `--help` output.
3. Do not add private endpoints, credentials, internal URLs, or dependencies
   that an agent would install silently.
4. Add or update tests for behavior changes, especially imports, consent, and
   secret handling.
5. Keep the Codex and Claude plugin versions aligned.

## Validate

From the Polygres monorepo root:

```bash
.venv/bin/python -m pytest packages/agent-skills/tests -q
.venv/bin/python -m ruff check packages/agent-skills
.venv/bin/python "$CODEX_HOME/skills/.system/skill-creator/scripts/quick_validate.py" \
  packages/agent-skills/plugins/polygres/skills/polygres-cli
.venv/bin/python "$CODEX_HOME/skills/.system/plugin-creator/scripts/validate_plugin.py" \
  packages/agent-skills/plugins/polygres
claude plugin validate packages/agent-skills
```

The two validator paths above are development-environment examples. Use the
current official validators in other environments.

## Security reports

Do not open a public issue containing a credential, access token, database
password, private endpoint, or sensitive customer data. Use GitHub private
vulnerability reporting when enabled, or the security contact published on
the Polygres website.
