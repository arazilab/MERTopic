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

- Use `templates/approved_summarization_embedding_pipeline.py` when embedding bullet summaries created from transcripts.
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

## Approved Embedding Pattern

For bullet embedding creation, follow `templates/approved_summarization_embedding_pipeline.py`.

Preserve these parts unless the dataset requires a small adaptation:

- validate that the bullet text column exists,
- fill missing text with an empty string before embedding,
- batch inputs with a configured batch size,
- use `tqdm` over batches,
- call `client.embeddings.create`,
- set model, dimensions, batch size, and encoding format from config,
- check that the embedding count equals the row count,
- save the embedding vectors in Parquet,
- save `embedding_model` and `embedding_dimensions`,
- save a CSV preview without the embedding vector column.

Dependency install pattern:

```bash
pip install -qqq openai pandas pyarrow tqdm python-dotenv
```

## Reuse

See `templates/common_code_patterns.md` for batching and record-linkage patterns.
