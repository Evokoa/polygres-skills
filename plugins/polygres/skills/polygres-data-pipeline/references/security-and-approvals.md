# Security, credentials, and approvals

## Create local credential files safely

Generate `.env.example` with required names and empty values. Ensure `.env` is
ignored by Git before the user adds credentials. Then tell the user:

```text
Change into the generated pipeline directory.
Run: cp .env.example .env
Open .env in your editor.
Paste each credential after its matching equals sign.
Save the file, but do not paste its contents into chat.
On macOS or Linux, run: chmod 600 .env
```

Typical local names are `POLYGRES_RUNTIME_URL`, `POLYGRES_API_KEY`, and a
source-specific name such as `SOURCE_DATABASE_URL` or `SOURCE_API_TOKEN`. Use
only names required by the selected adapter.

For managed PostgreSQL sync, do not generate or inspect a source credential
file. Direct the user to enter the source connection only in the Polygres
dashboard. Do not put that connection in chat, a plan, a CLI command, SDK code,
Runtime request, generated file, or log.

Run `scripts/check_env.py --env-file <path> --required <NAME>` for each required
name. The tool reports status without values. Do not open, print, summarize, or
log `.env`. For deployment, copy the same names into the platform secret
manager; do not upload `.env`.

If a user pastes a credential into chat, do not repeat it. Advise immediate
rotation and replacement in `.env`.

## Use one scoped mutation review

Build and test the local vertical slice first. Then show one compact review
covering the exact source scope, target project, data leaving the device, local
or hosted model, credential names, remote mutations, cost, reversibility, and
verification. Ask once before the first upload or remote mutation. An approval
of that displayed review covers the setup while its project, source scope, data
egress, destructive effects, and paid processing remain unchanged. Internal
implementation details may change without duplicate confirmation.

For a synced project, also disclose project mode, source authority, selected
tables and columns, continuous source-to-Polygres egress, Polygres-owned
publication and slot, reconfiguration behavior, and any resnapshot effect.

When an unknown embedding deployment preference leaves both local and hosted
paths feasible, fully describe one recommendation and one alternative inside
this review. A response selecting either described option is the one setup
approval. Do not show a second review unless that selection changes an
undisclosed material boundary.

Ensure the review includes any selected action in these categories:

- accessing additional private history or files;
- installing or upgrading software;
- downloading model weights or starting a persistent local service;
- sending content to a hosted provider;
- applying SQL or changing schema;
- importing or backfilling data;
- creating, updating, reindexing, or deleting Context resources;
- applying graph configuration or starting a build;
- installing a hook, wrapper, watcher, trigger, MCP configuration, or schedule;
- modifying an active `AGENTS.md` or equivalent agent instruction file;
- deploying a worker or changing an application write path;
- replacing data or changing retention and deletion behavior;
- creating or revealing a one-time secret;
- deleting source or derived data.

Ask again only when the project, source scope, data egress, destructive effects,
or paid processing changes. A different local implementation, file layout,
batch size, public client surface, or harmless rollback detail does not by
itself invalidate approval.

## Enforce authorization and privacy

Apply authorization before ingestion and before returning resolved rows. Do
not rely on filters alone. Exclude credentials, retrieved context, system
instructions, and unapproved tool or environment output. Preserve deletion
tombstones until derived cleanup is verified. Keep excluded content out of
logs and checkpoints.
