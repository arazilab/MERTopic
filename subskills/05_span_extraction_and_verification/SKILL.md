---
name: mertopic-span-extraction-and-verification
description: "Extract and verify verbatim spans or bullets for MERTopic workflows, including normalized exact-match verification, retry prompts, invalid-span tracking, and task-specific extraction objectives."
---

# Span Extraction And Verification

Use this sub-skill when the user wants grounded text units for thematic analysis.

## Goal

Extract verbatim spans or bullets, then verify that each one appears in the source text.

## Rules

- Normalize the text before matching.
- Verify every extracted span.
- Retry failed spans in the same conversation thread when possible.
- Expose retry count in config.
- Save unresolved invalid spans.
- Require a confirmed extraction objective before running if the workflow is construct-specific.
- Require API credentials and user approval before LLM extraction or summarization.
- Run a small sample first when the extraction objective is new or ambiguous.
- Stop for prompt review when sample spans are paraphrased, too broad, too narrow, or not exact matches.

## Do Not Proceed When

- the source text field is uncertain,
- the prompt permits paraphrase while downstream verification expects verbatim spans,
- the retry prompt is missing for exact-match workflows,
- previous relevancy or filtering outputs have not been inspected.

## Default Behavior

If the user does not specify a custom extraction objective:

- use a general extractive-summary prompt,
- require continuous spans,
- prohibit paraphrase.

If the user does specify a custom objective:

- adapt the prompt to that objective,
- keep the verification logic unchanged.

## Reuse

See:

- `templates/common_code_patterns.md`
- `templates/prompt_design_patterns.md`
