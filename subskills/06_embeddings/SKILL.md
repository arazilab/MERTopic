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

## Reuse

See `templates/common_code_patterns.md` for batching and record-linkage patterns.
