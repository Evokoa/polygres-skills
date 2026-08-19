# Embedding model selection

Use this only after semantic retrieval is selected. Model selection is part of
setup, not a separate interview.

## Inspect and rank silently

Infer these requirements from the prompt, bounded data sample, existing schema,
and application: languages, code content, maximum chunk length, commercial-use
constraint, existing vector dimensions, known provider or deployment preference,
and whether external processing is prohibited. Device feasibility is evidence,
not a statement that the user prefers local processing.

When local feasibility is relevant, run:

```sh
python3 scripts/check_embedding_device.py --json > device.json
python3 scripts/recommend_embedding_models.py \
  --requirements embedding-requirements.json \
  --device device.json
```

Use only the requirements that inspection established; these defaults form the
small complete object:

```json
{
  "deployment_preference": "unknown",
  "languages": ["en"],
  "max_chunk_tokens": 512,
  "contains_code": false,
  "commercial_use": true,
  "external_processing_allowed": true,
  "existing_dimensions": null,
  "preferred_runtime": null,
  "preferred_provider": null
}
```

The recommender reads the versioned `assets/embedding-models.json` catalog and
does not prompt, install, download, start services, inspect credential values,
or call a hosted provider. Treat its memory thresholds as conservative ranking
policy, then prove the chosen model with a small smoke test.

Prefer an already installed compatible model. Otherwise rank by hard
compatibility first: processing boundary, license, language, code, chunk length,
dimensions, disk, memory, and runtime. Use popularity only as a tie-breaker.
Never replace a pinned runtime model with a floating `latest` alias.

## Keep the user interaction to one review

- If the prompt, workspace, or existing configuration establishes local,
  hosted, or existing vectors, select an exact compatible model in that
  category. Ask no embedding-specific question. Include the model and its
  effects in the consolidated setup review.
- If preference is unknown and both paths are feasible, normally put at most
  one local recommendation and one hosted alternative in that same review.
  State which is recommended and why. The user's “approve recommended,” “use OpenAI
  instead,” or equivalent response both selects the fully described option and
  approves the review. Do not ask for a second approval.
- If hosted processing is prohibited, show only local. If local execution is
  infeasible, show only hosted. If compatible vectors already exist, recommend
  reuse. If semantic retrieval is unnecessary, omit embeddings entirely.
- Ask a new question only when neither safe path can be inferred, or when a
  later change introduces previously undisclosed egress, paid processing,
  destructive effects, project, or source scope.

The review must disclose exact model, provider, revision, dimensions, input
contract, normalization, credential names, filtered data egress, estimated
download, persistent service, and paid processing for every selectable option.
It must not display the internal requirements JSON, device report, catalog, or
ranking scores.

## Preserve the embedding contract

Store the selected provider, model, revision, dimensions, normalization,
document input, and query input in the pipeline configuration. Indexing and
querying must use the same contract. For model changes, use a new named vector
or a reviewed reindex rather than mixing vectors.

Before creating the final vector configuration or starting a backfill, embed a
small representative set of filtered records and queries. Five to 20 records is
a useful starting range, not a requirement. Verify the vector count,
finite values, exact dimensions, normalization, document/query formatting, a
simple relevant-result check, and acceptable local memory/latency or hosted
errors/rate handling. A failed candidate may fall back automatically only when
the alternative and all of its material effects were already included in the
approved review.

## Catalog maintenance

Catalog entries must cite provider or model-owner documentation and record the
date verified. Re-check mutable model availability, package size, context,
dimensions, license, API pricing, and provider contracts before publishing a
new skills release. Do not silently invent a provider alias or model contract
when documentation is unavailable.
