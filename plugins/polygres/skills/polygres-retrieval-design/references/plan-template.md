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

Choose relational, graph, vector, TSVector, fuzzy, or hybrid retrieval. Explain
why simpler alternatives are insufficient and call out any unsupported
strategy.

## Data model

Map tables, stable row IDs, relationships, direction, vector inputs,
dimensions, text sources, filters, and provenance fields.

## Configuration plan

Describe configuration values, readiness checks, rebuild or reindex triggers,
fallbacks, and the `$polygres-cli` handoff. Do not apply them.

## Application plan

Describe the `$polygres-sdk` calls, stage bounds, pagination, authorization,
deduplication, error handling, and token budget. Do not write production code.

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
