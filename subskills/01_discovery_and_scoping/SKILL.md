---
name: mertopic-discovery-and-scoping
description: "Scope a MERTopic project by inspecting text data, identifying ID/title/body/metadata fields, clarifying the research goal and unit of analysis, and deciding which topic-modeling pipeline stages are needed."
---

# Discovery And Scoping

Use this sub-skill first.

## Goal

Understand:

- what the data is,
- what fields exist,
- what the user is trying to learn,
- which pipeline stages are actually needed.

## Workflow

1. Inspect the files.
2. Identify likely ID, title, body, and metadata fields.
3. Estimate corpus size.
4. Ask only the minimum clarifying questions.

## Questions To Ask

- How was this dataset collected?
- What counts as a meaningful unit for analysis?
- Is there a focal construct or phenomenon?
- Is high recall more important than high precision in the first pass?
- Do you want a generic topic model or one tailored to a research question?

## Output

Write down:

- the proposed pipeline,
- which stages are optional,
- what will be stored in config,
- what the first runnable step will be.
