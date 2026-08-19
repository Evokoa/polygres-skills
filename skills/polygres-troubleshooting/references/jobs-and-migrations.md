# Jobs and migrations

Use public status commands after resolving the exact project:

```console
polygres --json --project <project> import status <job-id>
polygres --json --project <project> migrations list
```

For an import job, preserve the job ID, status, progress, structured error,
timestamps, and `request_id`. If no job ID was supplied, clearly label any
latest-job lookup and confirm it refers to the affected operation. Poll with a
bounded interval and timeout. Always check status before retry because a client
timeout can coexist with server-side success.

For a migration, compare local and reported migration identity without running
it. Separate malformed local metadata, checksum or compatibility mismatch,
Postgres rejection, and a control-plane or Runtime API transport failure.
Never repair history, apply a migration, or retry a partial failure during
diagnosis.

If progress is contradictory, stale, or missing, report the inconsistency and
escalate with the retained job and request IDs rather than guessing completion.
