---
name: polygres-retrieval-design
description: Design and review Polygres retrieval plans across relational, graph, pgvector, text, hybrid, and pgContext AI Search strategies. Use when a user must choose between retrieval surfaces, model graph or embedding inputs, plan Context collections or grounded RAG, or review retrieval architecture before configuration or implementation. Do not mutate a project, run configuration commands, or write application code.
---

# Polygres Retrieval Design

Produce a reviewable plan before retrieval configuration or application work.
This skill is advisory: it must not mutate a project directly.

## Workflow

1. Establish the user outcome, representative questions, authorization rules,
   latency target, freshness needs, and expected result shape.
2. Inspect the supplied schema, verified row identifiers, sample data, and
   existing retrieval configuration. Label missing evidence as unresolved;
   never infer production facts from a table or column name.
3. Select the smallest sufficient strategy using
   `references/strategy-selection.md`. Reject an unsupported strategy rather
   than inventing a capability.
4. For graph retrieval, apply `references/graph-modeling.md`. For vector,
   TSVector, or fuzzy retrieval, apply
   `references/vector-and-text-design.md`.
5. For pgContext collections, point synchronization, registered filters, or
   Context retrieval modes, apply `references/context-design.md`.
6. For multi-stage retrieval or RAG, apply
   `references/hybrid-and-rag-plan.md`.
7. Write the result with `references/plan-template.md`. Separate known facts,
   assumptions, decisions, risks, validation, and handoff work.
8. After explicit approval, delegate supported project configuration to
   `$polygres-cli` and application code to `$polygres-sdk`. Do not silently
   switch from planning to execution.

## Design rules

- Prefer relational retrieval for exact predicates, joins, aggregates, and
  transactions that do not need a retrieval index.
- Treat graph, vector, text, and Context indexes and point mappings as derived
  project resources whose readiness and refresh behavior must be validated.
- Use exact schema identifiers and stable row ID values from verified data.
  Do not use invented row IDs or fuzzy-match schema names.
- Bound graph direction, depth, fan-out, result count, and cycle behavior.
- Record the embedding model, dimensions, metric, input construction, and
  response to a dimension mismatch or empty embedding.
- Record whether pgvector configuration or pgContext collection semantics are
  required. Never treat those resources as interchangeable.
- State TSVector language/configuration choices and fuzzy thresholds.
- For hybrid retrieval, define stage order, provenance, deduplication,
  authorization, and token budget.
- Include rebuild or reindex triggers, readiness checks, and rollback or
  fallback behavior.

## Boundaries

- This skill must not mutate a project, generate secrets, or claim that a plan
  has been applied.
- Do not write mutating command examples. Route approved configuration work to
  `$polygres-cli` and approved Python integration to `$polygres-sdk`.
- Filters are not an authorization boundary. Apply access control before data
  enters retrieval and again when results are resolved.
- If required columns, stable IDs, representative queries, or a usable sample
  are absent, record the missing columns or empty sample and stop short of a
  final configuration recommendation.

## Completion

Return the completed reviewable plan, the unresolved assumptions, the
recommended public-surface handoffs, and the explicit approval needed before
any mutation or implementation.
