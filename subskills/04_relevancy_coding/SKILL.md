---
name: mertopic-relevancy-coding
description: "Build LLM-based relevancy coding for a MERTopic pipeline with narrow construct definitions, structured outputs, positive-case files, error preservation, progress reporting, and saved stats."
---

# Relevancy Coding

Use this sub-skill when lexical filtering is too broad and the user needs a narrower substantive subset.

## Goal

Use an LLM to decide whether a text is directly relevant to the target construct.

## Rules

- Keep the decision narrow.
- Use structured output.
- Save full results and positives separately.
- Keep errors in the dataset instead of silently dropping them.
- Show progress with `tqdm`.
- Require a confirmed construct definition before coding.
- Require a confirmed model and API credentials before running.
- Run a small sample first when the corpus is large or the construct is subtle.
- Save the sample outputs for user inspection before full-corpus coding when labels may be ambiguous.

## Do Not Proceed When

- the prompt is blank or only restates the column name,
- the inclusion and exclusion criteria are not clear,
- the user has not approved API use,
- `OPENAI_API_KEY` or the configured provider credential is unavailable,
- the input path does not match the previous stage's positive or filtered output.

## Prompt Design

The prompt should:

- define the target construct clearly,
- state what does not count,
- prohibit unsupported inference,
- specify the exact output format.

## Reuse

See:

- `templates/prompt_design_patterns.md`
- `templates/common_code_patterns.md`
