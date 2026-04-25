---
name: mertopic-analysis-tool-exports
description: "Export MERTopic outputs to annotation-style JSON and co-occurrence tables with one original-post record per source item, topic labels, topic IDs, context spans, and metadata."
---

# Analysis Tool Exports

Use this sub-skill when the user wants outputs for external browsing or co-occurrence tools.

## Goal

Convert topic-model outputs into annotation-style JSON and simple co-occurrence tables.

## Requirements

- Create one record per post.
- Always use the original post as the displayed text unit.
- Include `id` as the source post ID.
- Include `data` as the original title and body concatenated.
- Put assigned topics into an `annotation` list.
- Use human-readable topic labels directly in `annotation`.
- Add a `context` object that maps each annotation label to one or more exact spans from the original post.
- Use stable topic codes plus readable labels.
- Include enough source fields for browsing.
- Compute co-occurrence by counting one instance whenever two topics occur on the same post.

## Aggregation rule

- If the topic model was run at the post level, the post usually contributes one topic annotation.
- If the topic model was run at the bullet level, still export one record per original post.
- In the bullet-level case, aggregate all unique topics assigned to any bullet from the same post and attach them to that post record.

The analysis tools should therefore show original posts in both modes, while allowing either one topic or multiple topics to be attached.

## Output

Export:

- tool-compatible JSON,
- a topic index,
- a co-occurrence CSV,
- a small metadata file describing the export.
