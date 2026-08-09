# Retrieval plan template

## Outcome

State the user-visible question, answer shape, latency target, freshness, and
success measure.

## Known facts

List verified schema, representative data, stable IDs, current resources,
authorization constraints, and public interface compatibility.

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

## Application plan

Describe the exact public route or `$polygres-sdk` call, collection and exact
`vector_name` selection, stage bounds, pagination, authorization,
deduplication, error handling, and token budget. State that an omitted
`vector_name` selects the collection default, not the project default
collection. Do not write production code.

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
