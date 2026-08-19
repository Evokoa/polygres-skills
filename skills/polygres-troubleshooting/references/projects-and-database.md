# Projects and database

After resolving one exact project, collect public read-only status:

```console
polygres --json --project <project> projects status
polygres --json --project <project> ready
```

Read `project_mode` from status before continuing. For a standard project, add
`polygres --json --project <project> db info`. For a synced project, never run
`db info`; follow `synced-projects.md` and keep source, control-plane, and
Runtime evidence separate.

`projects status` can separate provisioning or control-plane state from Runtime
API readiness and resource pressure. Preserve its `request_id`. Record
readiness fields and public storage and memory observations without inferring
private infrastructure details. A project in `read_only` state may reject
writes while still answering reads.

`db info` provides public connection metadata. Distinguish a direct database
endpoint from the pooler and Runtime API. Do not display or request a database
password. For Postgres failures, preserve the SQLSTATE or sanitized client
error, endpoint class, TLS mode, and whether the failure occurred before or
after authentication.

Treat one failed surface independently: a healthy control-plane response does
not establish database, pooler, or Runtime API health. A timeout may leave the
server-side result unknown, so re-check status before retry.
