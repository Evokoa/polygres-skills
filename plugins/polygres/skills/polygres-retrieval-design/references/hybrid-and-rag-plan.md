# Hybrid and RAG plan

Use hybrid retrieval only when the representative questions require more than
one evidence mode.

## Stage design

Choose and justify one flow:

- Relational filters followed by vector or text ranking.
- Vector or text candidates followed by graph expansion.
- Graph anchors followed by vector ranking.
- Independently retrieved candidates merged by an explicit scoring rule.

For every stage, define its inputs, bounds, timeout, failure behavior, and the
stable row ID used to join results. Preserve provenance: strategy, source
table, row ID, score, graph path, relationship direction, and configuration
version where available.

## Grounding controls

Apply authorization before candidate generation and when resolving final
rows. Deduplicate by verified identity, not display text. Define ordering after
deduplication, per-source and total token budget, truncation behavior, and the
minimum evidence needed to answer. Never present partial failure as complete
coverage.

Include readiness checks for every required resource and state which rebuild
or reindex event invalidates the plan. If one stage is unavailable, specify a
safe degraded mode or return a clear unavailable result rather than silently
changing retrieval semantics.
