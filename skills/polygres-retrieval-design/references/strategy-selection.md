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

If the request requires an unsupported strategy, mark it as unsupported and
offer the nearest public alternative. If there is an empty sample, missing
columns, unknown authorization model, or no representative queries, preserve
that uncertainty instead of pretending the plan is production-ready.
