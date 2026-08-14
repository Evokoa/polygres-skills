# Internal setup plan and safety lint

The plan is private working state for the agent, not a user deliverable or a
fixed schema. Use the smallest JSON object that helps resume multi-step work.
A simple setup can record only source, target, actions, approval, and
verification. Skip the plan entirely for a harmless one-step check.

Add schema, embeddings, graph, backfill, incremental capture, retrieval,
deployment, or agent integration only when selected. Missing optional details
must not create user questions.

Record defaults as inferred choices, not universal requirements. The agent may
change their order, values, or implementation as evidence improves without
invalidating approval unless project, source scope, data egress, destructive
effects, or paid processing changes. A component marked `enabled: false` is
intentionally omitted and must not produce scaffold files or review noise.

## Quiet lint

Run this internally:

```text
python3 scripts/validate_pipeline_plan.py plan.json
```

It returns JSON with `blockers` and `warnings`. Automatically correct blockers
from inspected evidence when possible. Resolve or accept warnings silently.
Never show raw lint output or ask the user to edit `plan.json`.

Only these conditions block:

1. a remote mutation has no resolved Polygres project;
2. the plan contains a credential or secret value instead of an environment
   variable name;
3. an existing approval no longer matches project, source scope, data egress,
   destructive actions, or paid processing;
4. capability evidence says a selected public interface is unavailable;
5. the plan claims `operational` without passing evidence for the important
   path.

Everything else is optional or a warning.

## Actions and capabilities

For an intended remote mutation, set `remote_mutation: true` or use a known
remote action type. Useful action fields are `id`, `type`, `effect`, `target`,
`data_egress`, `destructive`, and `paid_processing`. Rollback and dependency
details are useful for risky work but unnecessary for harmless local actions.

A selected interface can record `surface`, `operation`, `capability`, and
`available`. Capability discovery may instead populate a top-level
`capabilities` map. `available: false` blocks use; unknown availability warns
the agent to check without questioning the user.

## One approval boundary

Render one concise review internally with:

```text
python3 scripts/render_pipeline_review.py plan.json
```

After the user approves it, store `approval.status: approved` and the printed
digest as `approval.boundary_digest`. This digest intentionally covers only:

- project;
- source scope;
- data egress;
- destructive effects;
- paid processing.

Implementation details may evolve without another approval. Ask again only
when one of those five boundaries changes.

When two embedding paths are offered, record at most the fully reviewed local
and hosted choices in `embedding_options` and the preferred model ID in
`recommended_embedding_id`. The approval boundary includes the egress and paid
processing of both. Keep these reviewed options after selection so choosing the
other disclosed path does not manufacture a stale approval.

## Verification

Before setting `state: operational`, record either
`verification.important_path` or a claim named `important-path`,
`vertical-slice`, or `end-to-end`, with passing status and concrete evidence.
Do not require representative questions or tests for components that were not
selected.
