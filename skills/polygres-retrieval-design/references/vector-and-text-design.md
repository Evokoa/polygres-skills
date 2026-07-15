# Vector and text design

## Vector retrieval

Record the embedding model, exact dimensions, distance metric, input template,
normalization, metadata columns, filters, result limit, and minimum score.
Confirm that stored and query embeddings use the same model and dimensions.
Treat a dimension mismatch, malformed vector, or empty embedding as a blocked
input, not a zero vector or retryable success.

State which source changes require a reindex, how readiness is checked, and
what relational or text fallback is safe while the index is unavailable.
Plan tests for duplicate content, deleted rows, filter interactions, empty
queries, extreme lengths, and model-version compatibility mismatches.

## Text retrieval

For TSVector, record the source columns, weights, language configuration,
normalization, ranking, prefix behavior, and candidate cap. Test punctuation,
stop words, Unicode, empty input, and missing columns.

For fuzzy retrieval, record normalization, similarity threshold, indexed
columns, candidate cap, and an exact-match preference. Include noisy, short,
Unicode, and adversarial strings. Fuzzy matching is for user data, never to
fuzzy-match schema identifiers or silently select a project resource.
