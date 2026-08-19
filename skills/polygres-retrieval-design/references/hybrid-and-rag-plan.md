# Hybrid and RAG plan

Use hybrid retrieval only when the representative questions require more than
one evidence mode.

For new vector-backed or composed retrieval, use pgContext. Plain dense and
grouped retrieval use `/context/search` and `/context/grouped-search`;
composition uses the public `/context/hybrid/text`,
`/context/hybrid/graph-first`, `/context/hybrid/vector-first`,
`/context/hybrid/rank-fusion`, or `/context/hybrid/joint` route that matches the
stage design. Do not choose the Legacy `/hybrid/*` surface for a new design.

Treat Legacy Hybrid as existing-only. It is usable only with a persisted,
enabled Legacy vector registration whose effective state is Ready, plus every
other required resource. For `index_kind: hnsw`, the exact configured physical
index must be Ready. For `index_kind: none`, a verified registration can be
Ready for exact-scan retrieval without HNSW. A physical-only pgvector index is
never an implicit registration, and the retired Legacy APIs cannot register or
re-enable one.

## Stage design

Choose and justify one flow:

- Relational authorization and filters followed by pgContext dense or text
  ranking.
- pgContext vector candidates followed by graph expansion with
  `/context/hybrid/vector-first`.
- Graph anchors followed by pgContext ranking with
  `/context/hybrid/graph-first`.
- Independently retrieved Context and graph candidates combined with
  `/context/hybrid/rank-fusion`.
- A coupled graph expansion, exact Context rescoring, and final fusion flow with
  `/context/hybrid/joint` when graph traversal must introduce candidates.

For every stage, define its inputs, bounds, timeout, failure behavior, and the
ordered stable identity used to join results. Preserve provenance: strategy,
source table, every identity component in order, score, graph path,
relationship direction, and configuration version where available.

## Grounding controls

Apply authorization before candidate generation and when resolving final
rows. Deduplicate by verified identity, not display text. Define ordering after
deduplication, per-source and total token budget, truncation behavior, and the
minimum evidence needed to answer. Never present partial failure as complete
coverage.

Include readiness checks for every required resource and state which rebuild
or reindex event invalidates the plan. If one stage is unavailable, specify a
safe degraded mode or return a clear unavailable result rather than silently
changing retrieval semantics. Never fall back from Context to a physical-only
or disabled Legacy vector configuration.
