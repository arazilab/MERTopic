---
name: mertopic-embeddings
description: "Generate traceable embeddings for MERTopic verified spans, bullets, and post-level summaries with source IDs, bullet IDs, model metadata, batching, previews, and stats."
---

# Embeddings

Use this sub-skill after verified spans or bullets are available.

## Goal

Create:

- one embedding per verified span or bullet,
- one embedding per post-level concatenation of verified spans.

## Requirements

- Preserve source post IDs.
- Preserve bullet IDs.
- Store embedding model and dimensions.
- Save preview files and stats.
- Use batching and `tqdm`.
- Require API credentials and user approval before running embedding calls.
- Check that the input text unit matches the planned topic-modeling level.
- Write enough metadata to reproduce the embedding run: model, dimensions, encoding format, batch size, input path, row count, timestamp, and script version when available.

## Stop Gate

Before embedding, report:

- input file and row count,
- text field to embed,
- model and dimensions,
- estimated number of API calls or batches,
- output files.

Proceed only after confirmation when the user requested stage-by-stage control.

## Reuse

See `templates/common_code_patterns.md` for batching and record-linkage patterns.
