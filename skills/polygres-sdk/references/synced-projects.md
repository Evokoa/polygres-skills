# Synchronized PostgreSQL projects

## Initialize the mode-aware client

Use SDK 0.4.0 or newer when local mode-aware protection is required:

```python
import os

from polygres import Polygres

client = Polygres(
    api_key=os.environ["POLYGRES_API_KEY"],
    runtime_url=os.environ["POLYGRES_RUNTIME_URL"],
)
project = client.project(project_mode="synced")
```

Keep `POLYGRES_API_KEY` and `POLYGRES_RUNTIME_URL` in trusted server-side
configuration. A synced-project key authenticates only the project Runtime API.
It cannot authenticate project creation, source preflight, table selection,
reconfiguration, pause, resume, retry, resnapshot, or credential work.

Do not build control-plane requests with the SDK. Direct interactive sync setup
and lifecycle work to the dashboard. Never receive or pass the source database
URL or password through application code generated for the Runtime SDK.

## Use only supported Runtime surfaces

Use graph, text, existing vector, hybrid, Context, retrieval readiness, and the
table catalog where a public SDK method exists. Do not call:

- `project.rows.validate()`, `insert()`, `upsert()`, or `ignore()`;
- `project.connection_info()`;
- imports, migrations, SQL, or target database connection paths.

The Runtime returns `PolygresPermissionError` with
`SYNCED_PROJECT_SURFACE_UNAVAILABLE` for a prohibited surface. Treat it as an
intentional project-mode boundary. Do not retry or probe nearby endpoints.
Without the local `project_mode` hint, the server remains authoritative.

## Write and embed at the source

Write, update, delete, and generate embeddings in the source PostgreSQL
database. Managed snapshot and logical replication carry eligible changes into
Polygres. Do not treat filters as an authorization boundary.

For pgContext, create or use a collection over an existing synchronized table
and embedding column. Do not select `new_table` or `add_column` on a synced
target. Polygres does not generate embeddings.

Use graph relationships only when both foreign-key endpoint tables are in the
sync selection. Preserve synchronized source row IDs as retrieval provenance.

## Report completion accurately

State that the project mode is synced, name the Runtime retrieval surfaces
used, and identify source-database changes separately. Do not claim that SDK
code created, configured, paused, resumed, repaired, or rotated the sync.
