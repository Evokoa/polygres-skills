# Contributing

The canonical source for this package is `packages/agent-skills` in the private
Polygres monorepo. The public repository is generated from that directory, with
deterministic `skills/<skill-name>` discovery mirrors added during export. Do
not maintain a separate hand-edited public copy.

## Change a skill

1. Keep the core `SKILL.md` concise and move detailed workflows into focused
   references.
2. Verify CLI examples against the current parser and installed `--help`, and
   SDK examples against the current public Python signatures.
3. Do not add private endpoints, credentials, internal URLs, or dependencies
   that an agent would install silently.
4. Add or update unit tests for every behavior change. Mark cross-package,
   installed-package, or live-agent checks as `heavy`.
5. Keep the Codex and Claude plugin versions aligned.

## Validate

From the Polygres monorepo root:

```bash
python -m pytest packages/agent-skills/tests -m "not heavy" -q
python -m pytest packages/agent-skills/tests -m heavy -q
python packages/agent-skills/scripts/validate_package.py packages/agent-skills
python packages/agent-skills/scripts/export_public.py \
  packages/agent-skills /tmp/polygres-skills-export
.venv/bin/python -m ruff check packages/agent-skills
for skill in packages/agent-skills/plugins/polygres/skills/*; do
  .venv/bin/python "$CODEX_HOME/skills/.system/skill-creator/scripts/quick_validate.py" \
    "$skill"
done
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
