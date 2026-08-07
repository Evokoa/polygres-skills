# Strategy selection

Choose the smallest strategy that answers the representative questions.

| Need | Prefer | Review constraints |
| --- | --- | --- |
| Exact filters, joins, aggregates, ordering, or transactions | relational | indexes, query plan, cardinality, authorization |
| Traversal through explicit relationships | graph | stable row ID, direction, bounded depth, fan-out, cycles |
| Semantic similarity | vector | embedding model, dimensions, metric, filters, reindex policy |
| Lexical relevance | TSVector | language configuration, ranking, indexed source columns |
| Typo-tolerant names or short labels | fuzzy | threshold, normalization, candidate cap, false positives |
| Multiple evidence modes | hybrid | stage order, provenance, deduplication, token budget |
| Managed AI Search collection with point lifecycle, registered filters, recall checks, or Context plus graph/text composition | pgContext | native Context vectors, source mode, reconciliation, capability status, preview contract |

## Decision procedure

1. Write representative queries and the required answer shape.
2. Identify exact constraints that belong in relational predicates regardless
   of the retrieval strategy.
3. Select graph only when explicit relationships and bounded traversal add
   information. Select vector only when semantic similarity is necessary.
4. Select TSVector for linguistic ranking and fuzzy retrieval only for
   deliberate typo tolerance. Do not use fuzzy-match schema discovery.
5. Select hybrid only when a single mode demonstrably misses required
   evidence. Define which stage supplies candidates and which stage reranks or
   expands them.
6. Select pgContext when collection identity, native Context vectors, durable
   point reconciliation, registered filters, recall validation, or Context
   graph/text composition are requirements. Prefer the existing pgvector-backed
   vector surface for a simple established pgvector configuration that does not
   need those collection semantics.

A pgvector configuration ID cannot be used as a pgContext collection. Record a
migration or coexistence plan when both surfaces are present; do not imply an
automatic conversion or fallback.

If the request requires an unsupported strategy, mark it as unsupported and
offer the nearest public alternative. If there is an empty sample, missing
columns, unknown authorization model, or no representative queries, preserve
that uncertainty instead of pretending the plan is production-ready.
