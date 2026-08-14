---
name: polygres-troubleshooting
description: Diagnose Polygres CLI, Runtime API, control-plane, Postgres, job, migration, retrieval, and pgContext failures using public read-only evidence. Use for errors, timeouts, partial failures, readiness problems, ambiguous projects, failed Context collections or operations, stale point mappings, or broken graph, vector, text, hybrid, or Joint retrieval. Do not use private observability, undocumented endpoints, or mutating repair actions.
---

# Polygres Troubleshooting

Use read-only checks first. Resolve context, preserve evidence, classify the
failure boundary, and recommend the smallest safe correction. Do not mutate
while diagnosing.

## Workflow

1. Read the installed `polygres --help` and command-specific help before using
   a command. Installed behavior is the source of truth for CLI compatibility.
2. Resolve identity, configuration source, and one exact project using
   `references/context-and-connectivity.md`. Stop on an ambiguous project.
3. Capture the symptom, timestamp, sanitized command or SDK call, exit code or
   exception type, `request_id`, job ID, and whether pagination returned a
   cursor.
   For generated pipelines, also capture the manifest state, plan digest,
   approved action IDs, checkpoint, and last successfully completed stage.
4. Inspect project and database evidence with
   `references/projects-and-database.md`.
5. For import job or migration failures, use
   `references/jobs-and-migrations.md`. For graph, vector, text, hybrid, or
   general readiness failures, use `references/retrieval.md`. For pgContext
   capability, collection, point, operation, recall, or Joint failures, use
   `references/context.md`.
6. Classify the fault as CLI/local configuration, control-plane, Runtime API,
   Postgres/database or pooler, or asynchronous job state. Use
   `references/errors-and-escalation.md` for typed SDK errors and escalation.
7. Re-check status before retry. Recommend a corrective action, but obtain
   explicit approval and delegate supported mutations to `$polygres-cli` or
   application changes to `$polygres-sdk`.

For a single-row write that lost the response after submission, treat the
commit outcome as ambiguous unless public evidence resolves it. Do not
automatically retry a row-only insert, upsert, or ignore. For a Context-backed
write, replay the exact request with its exact idempotency key within the
24-hour replay window; the composite ledger prevents another row mutation.
After `ROW_CONTEXT_IDEMPOTENCY_EXPIRED`, inspect the row and Context point before
choosing a new key.

## Evidence rules

- Use only commands confirmed by installed help and public `$polygres-sdk`
  methods. Never guess a private endpoint or use internal observability.
- Preserve request and job IDs exactly. Distinguish absent evidence from a
  successful check.
- Never log a database password, API key, authorization header, connection
  string containing credentials, or full environment output.
- Do not retry validation, authentication, permission, or compatibility errors
  as if they were transient. Bound any retry for a rate limit or timeout.
- Do not request approval again for a corrective action already covered by an
  unchanged consolidated pipeline review. Ask again when its project, source
  scope, action set, egress, destructive effect, or plan digest changed.
- Report pagination and partial failure explicitly; a successful first page or
  one healthy subsystem does not prove the whole operation succeeded.

## Diagnostic report

- **Resolved identity:** account identity or the exact reason it is unknown.
- **Resolved project:** exact project ID or the ambiguity that blocked selection.
- **Symptom:** observable failure and affected operation.
- **Observed evidence:** sanitized statuses, exception classes, and timestamps.
- **Likely cause:** evidence-backed classification with confidence.
- **Safe checks performed:** public read-only commands and SDK calls used.
- **Corrective action:** smallest documented action, not yet performed.
- **Approval or escalation:** approval needed or escalation destination.
- **IDs retained:** request IDs, job IDs, and cursors without secrets.
- **Unknowns:** missing, stale, incompatible, or contradictory evidence.

## Boundaries

- Do not mutate while diagnosing, rotate credentials, retry jobs or Context
  operations, apply migrations, reconcile points, rebuild graph resources, or
  start a text, vector, or Context reindex.
- Do not call an undocumented or private route and do not query a private
  observability system.
- Do not claim root cause when evidence supports only a likely boundary.
