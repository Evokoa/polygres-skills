---
name: polygres-retrieval-design
description: Design and review Polygres retrieval plans across relational, graph, text, hybrid, Polygres AI Context, and existing pgvector-backed strategies. Use when a user must choose between retrieval surfaces, model graph or embedding inputs, plan Context collections or grounded RAG, migrate or coexist with an existing vector configuration, or review retrieval architecture before configuration or implementation. Do not mutate a project, run configuration commands, or write application code.
---

# Polygres Retrieval Design

Produce a reviewable plan before retrieval configuration or application work.
This skill is advisory: it must not mutate a project directly.

## Workflow

1. Extract the user outcome, authorization, latency, freshness, and expected
   result shape from the prompt and inspected application. Ask only for a
   missing fact that changes the recommendation; representative questions are
   useful evidence, not a mandatory interview.
2. Resolve project mode, then inspect the supplied schema, verified row identifiers, sample data, and
   existing retrieval configuration. Label missing evidence as unresolved;
   never infer production facts from a table or column name.
3. Select the smallest sufficient strategy using
   `references/strategy-selection.md`. Reject an unsupported strategy rather
   than inventing a capability.
4. For graph retrieval, apply `references/graph-modeling.md`. For an existing
   vector configuration, TSVector, or fuzzy retrieval, apply
   `references/vector-and-text-design.md`.
5. For pgContext collections, point synchronization, registered filters, or
   Context retrieval modes, apply `references/context-design.md`.
6. For multi-stage retrieval or RAG, apply
   `references/hybrid-and-rag-plan.md`.
7. Write the result with `references/plan-template.md`. When called by
   `$polygres-data-pipeline`, return the selected and omitted components plus
   exact public-interface handoffs in a machine-readable section so the caller
   can continue without another interview.
8. In a design-only request, stop before mutation. In an active data-pipeline
   setup, return control to the orchestrating skill; its consolidated review
   and approval govern the implementation.

## Design rules

- Prefer relational retrieval for exact predicates, joins, aggregates, and
  transactions that do not need a retrieval index.
- For a synced project, keep exact SQL, transactions, and source mutations in
  the source PostgreSQL database. Use only the supported Runtime retrieval and
  retrieval-configuration surfaces on Polygres.
- Treat graph, vector, text, and Context indexes and point mappings as derived
  project resources whose readiness and refresh behavior must be validated.
- Use exact schema identifiers and stable row ID values from verified data.
  Do not use invented row IDs or fuzzy-match schema names.
- Bound graph direction, depth, fan-out, result count, and cycle behavior.
- Record the embedding model, dimensions, metric, input construction, and
  response to a dimension mismatch or empty embedding.
- Default new semantic retrieval plans to a Polygres AI Context collection.
  Decide explicitly whether distinct embeddings belong as named vectors in one
  collection or require separate collection-level source and policy settings.
  Record any existing pgvector configuration that must remain compatible or
  needs a migration plan. Never treat those resources as interchangeable.
  On a synced project, use only an existing synchronized source table and
  embedding column; do not plan `add_column` or `new_table` on the target.
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
- If required columns, stable IDs, or a usable sample are absent, make a
  reversible provisional recommendation when possible. Stop only when the
  missing evidence makes every safe recommendation invalid.

## Completion

Return the completed reviewable plan, the unresolved assumptions, the
recommended public-surface handoffs, and the explicit approval needed before
any mutation or implementation.
