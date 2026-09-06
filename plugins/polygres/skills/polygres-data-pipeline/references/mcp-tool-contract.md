<!-- Generated from ../../../references/mcp-tool-contract.md; source-sha256: e85bd5a12eb91ea734fdd2638849e14ec2418722f10623ac9d630fe19c91d7ac -->

# Polygres MCP tool contract

Contract version: `1.0`

Skills package compatibility: `0.6.0`

## Contents

- Connect and discover
- Common execution flow
- Tool catalog by feature group
- Bounds and results
- Complementary surfaces

## Connect and discover

Use the MCP tools already available in the current agent session. Treat the
discovered catalog as authoritative for that connection.

Canonical URLs:

- local: `http://127.0.0.1:8080/mcp`
- staging: `https://mcp.staging.polygres.com/mcp`
- production: `https://mcp.polygres.com/mcp`

The connection URL accepts `project_id`, `read_only=true`, and a comma-separated
`features` subset. Feature values are `projects`, `database`, `imports`, `sync`,
`context`, `graph`, `debugging`, and `docs`.

Call `whoami` first. In fixed-project mode, project-scoped tool schemas hide
`project_id` and the server injects the approved project. In multi-project mode,
pass one exact `project_id` on every project-scoped call. The server does not
keep a mutable default project.

The visible catalog is the intersection of connection features, read-only
mode, installation scopes, current role permissions, project access, project
mode, project state, and catalog version. A missing tool is unavailable in the
current connection. Use the documented CLI, SDK, or Dashboard fallback instead
of calling it by name.

## Common execution flow

1. Inspect discovered tools and, when reachable, `/compatibility`.
2. Call `whoami` and resolve the project boundary.
3. Use `get_project` or `get_project_status` to resolve project mode and state.
4. Perform the smallest bounded read-only inspection.
5. Choose the required components and prepare exact arguments and stable
   idempotency keys.
6. Present one consolidated review for the unchanged mutation set.
7. Call each selected mutation. When it returns `status: action_required`, show
   `proposed_action` and `confirmation_class` to the user.
8. After approval, replay the unchanged call with the exact server-returned
   `action_digest` in `confirmation`.
9. Preserve resource, request, job, and operation IDs. Observe durable work with
   `wait_for_operation` or the matching status tool.
10. Verify one serving-path result and report terminal, partial, or nonterminal
    state from observed evidence.

Never calculate an action digest. A change to tool, project, or arguments needs
a new proposal. Reuse the same idempotency key after an ambiguous response to
the same intended mutation. Use a new key for a new action.

## Tool catalog

### Identity and projects

- Read: `whoami`, `list_projects`, `get_project`, `get_project_status`,
  `get_project_creation_options`, `preview_capacity_upgrade`, `list_operations`,
  `get_operation`, `wait_for_operation`
- Write confirmation: `create_standard_project`,
  `retry_project_provisioning`, `create_capacity_upgrade_quote`,
  `cancel_operation`, `retry_operation`
- External-financial confirmation: `upgrade_project_capacity`
- `list_projects`, project creation, synchronized preflight, and table selection
  are multi-project tools and stay hidden in fixed-project mode.
- `list_operations` supports `context` and `import`. `get_operation` and
  `wait_for_operation` support `context`, `import`, `graph`, and `sync`.
  Cancellation supports `context` and `import`; retry supports `context`.

### Standard-project database rows

- Read: `list_tables`, `read_table_rows`
- Validation: `validate_row_write`
- Bounded write: `upsert_row`

These tools require a standard project. `upsert_row` always uses upsert mode and
requires an idempotency key. Use CLI or SDK for insert and ignore modes.

### Dashboard-started imports

- Read: `list_imports`, `get_import`
- Destructive confirmation: `cancel_import`

The Dashboard owns file selection, upload, preview, configuration, and job
start. These tools require a standard project.

### Synchronized projects

- Setup read: `get_synchronized_project_preflight`,
  `list_synchronized_source_tables`
- Setup write confirmation: `select_synchronized_tables`,
  `create_synchronized_project`
- Lifecycle read: `get_synchronization_status`
- Lifecycle write confirmation: `pause_synchronization`,
  `resume_synchronization`, `retry_synchronization`
- Destructive confirmation: `resnapshot_synchronization`

Source credentials are entered in the Dashboard. Runtime rows, imports,
migrations, and target database access are standard-project surfaces. Writes
for synchronized projects remain in the source PostgreSQL database.

### Polygres AI Search

- Collection and point reads: `get_context_capabilities`,
  `discover_context_sources`, `preflight_context_collection`,
  `list_context_collections`, `get_context_collection`,
  `get_context_collection_status`, `verify_context_collection`,
  `get_context_index_status`, `list_context_filters`,
  `get_context_point_status`, `list_context_points`
- Retrieval: `context_search`, `search_full_text`,
  `context_text_hybrid_search`, `hybrid_search`,
  `context_graph_first_search`, `context_first_graph_search`,
  `context_rank_fusion_search`, `context_joint_search`,
  `group_context_results`, `count_context_points`, `get_context_facets`,
  `recommend_context_records`, `explore_context_records`,
  `explain_context_query`, `check_context_recall`
- Write confirmation: `create_context_collection`,
  `update_context_collection`, `reindex_context_collection`,
  `add_context_filter_column`, `add_context_filter_jsonb_path`,
  `upsert_context_points`, `reconcile_context_points`
- Destructive confirmation: `delete_context_collection`,
  `delete_context_points`
- Resource-intensive confirmation: `backfill_context_points`

Hybrid calls that traverse graph require both Context-read and Graph-read
installation scopes. The caller generates source and query embeddings.

### Graph

- Read: `discover_graph_schema`, `get_graph_configuration`,
  `get_graph_status`, `get_graph_system`, `expand_graph`,
  `get_graph_neighborhood`, `find_related_records`, `find_graph_path`,
  `find_graph_connection`
- Write confirmation: `configure_graph`, `update_graph_system`
- Resource-intensive confirmation: `build_graph`, `run_graph_maintenance`

Use verified table identifiers and relationships. Bound direction, depth,
fan-out, filters, and result count.

### Diagnostics

- `get_retrieval_readiness`, `get_context_diagnostics`,
  `get_context_index_diagnostics`, `get_context_index_advice`,
  `get_context_query_stats`, `get_project_capacity`,
  `get_project_storage_usage`, `get_project_metrics`,
  `get_project_metrics_history`

Diagnostics expose bounded public project evidence. Preserve request IDs.

### Public documentation

- `search_docs`, `get_doc`

Use these for the versioned documentation bundled with the MCP release.

## Bounds and results

Inputs reject unknown fields. JSON input and output are bounded to one MiB,
12 nesting levels, 512 object fields, 10,000 list items, and 100,000 characters
per string. Page limits are normally 1 through 100. `wait_for_operation` accepts
1 through 30 seconds and a poll interval from 0.5 through 5 seconds.

Public failures contain a stable error code, retryable flag, and request ID.
Retry rate limits and temporary network or service failures within the stated
bound. Resolve validation, authentication, permission, project-boundary,
project-mode, and compatibility failures before another call.

## Complementary surfaces

Use the CLI for migrations, Runtime keys, interactive database access, import
start, and operations absent from the discovered catalog. Use the Python SDK
for persistent application integration. Use the Dashboard for source secret
entry, CSV upload and import start, project deletion, and project pause or
restore. Keep existing pgvector and legacy hybrid integrations on their public
CLI, SDK, or Runtime interfaces.

MCP excludes arbitrary SQL, migrations, Runtime keys, database passwords,
project deletion, project pause or restore, legacy vector and hybrid routes,
Context model registration, embedding migration, bulk Context deletion,
third-party embedding or reranking calls, private observability, and operator
infrastructure.
