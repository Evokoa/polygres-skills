# Retrieval plan template

## Outcome

State the user-visible question, answer shape, latency target, freshness, and
success measure.

## Known facts

List project mode, verified schema, representative data, stable IDs, current resources,
authorization constraints, and public interface compatibility.

For a synced project, also list the source system of record and selected
tables and columns. State that source credentials were not collected.

## Unresolved assumptions

List every unknown, missing column, empty sample, ambiguous identifier, or
compatibility question and the evidence needed to resolve it.

## Strategy decision

Choose relational, graph, TSVector, fuzzy, pgContext dense or grouped search,
or pgContext composition. For composition, name the exact
`/context/hybrid/*` route. Use generic vector or Legacy Hybrid only for an
existing persisted registration that is effectively Ready; do not propose it
for a new vector-backed design. Explain why simpler alternatives are
insufficient and call out any unsupported strategy.

## Data model

Map tables, ordered non-empty `id_columns`, relationships, direction,
collection and vector names, collection-default and project-default choices,
vector inputs, dimensions, metrics, `index_kind`, text sources, filters, and
provenance fields. Treat singular `id_column` as deprecated compatibility input
for one identifier column.

## Configuration plan

Describe configuration values, readiness checks, rebuild or reindex triggers,
fallbacks, and the `$polygres-cli` handoff. For Context, distinguish
`index_kind: hnsw` physical-index readiness from `index_kind: none` exact-scan
readiness. If an existing pgvector column will become a Context vector, include
preflight and explicitly approved Legacy registration cleanup before creation;
the dashboard does not do this automatically. Never treat a physical-only index
as implicitly usable or propose a retired Legacy API to register or re-enable
it. Do not apply the plan.

For a synced project, use existing synchronized source columns only. Identify
selection changes that trigger reinspection, resync, or retrieval revalidation.

## Application plan

Describe the exact public route or `$polygres-sdk` call, collection and exact
`vector_name` selection, stage bounds, pagination, authorization,
deduplication, error handling, and token budget. State that an omitted
`vector_name` selects the collection default, not the project default
collection. Do not write production code.

For a synced project, separate source-database SQL and writes from Polygres
Runtime retrieval. Do not assign sync control-plane work to the API key, CLI,
or SDK.

## Validation plan

Cover representative queries, empty and malformed inputs, fuzzy data, missing
resources, incompatible dimensions, timeouts, partial failures, provenance,
and result quality.

## Risks and approvals

Record data exposure, cost, latency, stale-index, migration, and rollback risks.
Name the explicit approval required before configuration or implementation.

## Handoff

Separate project configuration for `$polygres-cli`, application work for
`$polygres-sdk`, owners, sequencing, and remaining unknowns.

When this plan is consumed by `$polygres-data-pipeline`, append JSON with this
shape so implementation can continue without re-asking resolved questions:

```json
{
  "selected_components": ["text", "context", "retrieval_runtime"],
  "omitted_components": {"graph": "no useful relationship evidence"},
  "interfaces": {
    "retrieval": {"surface": "sdk", "operation": "project.context.search"}
  },
  "blocking_unknowns": []
}
```

Include only selected components and public operations. This handoff is design
evidence, not mutation approval.
