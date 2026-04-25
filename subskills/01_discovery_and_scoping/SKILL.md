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
5. Stop for scope confirmation before writing pipeline code unless the user explicitly requested no planning pause.

## Hard Stops

- Do not scaffold scripts before the dataset shape and analytic goal are understood.
- Do not choose LDA, NMF, or another fallback topic model because it is easier to run locally.
- Do not infer a sensitive or theory-heavy research construct from column names alone.
- Do not proceed to API stages until credentials and permission are confirmed.

## Questions To Ask

- How was this dataset collected?
- What counts as a meaningful unit for analysis?
- Is there a focal construct or phenomenon?
- Is high recall more important than high precision in the first pass?
- Do you want a generic topic model or one tailored to a research question?
- Should I create runnable scripts and stop for you to execute them, or run confirmed stages directly when credentials are available?

## Output

Write down:

- the proposed pipeline,
- which stages are optional,
- what will be stored in config,
- what the first runnable step will be,
- which exact user answers are still needed before implementation.
