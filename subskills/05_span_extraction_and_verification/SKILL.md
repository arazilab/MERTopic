---
name: mertopic-span-extraction-and-verification
description: "Extract and verify verbatim spans or bullets for MERTopic workflows, including normalized exact-match verification, retry prompts, invalid-span tracking, and task-specific extraction objectives."
---

# Span Extraction And Verification

Use this sub-skill when the user wants grounded text units for thematic analysis.

## Goal

Extract verbatim spans or bullets, then verify that each one appears in the source text.

## Rules

- Use `templates/approved_summarization_embedding_pipeline.py` when the user wants transcript summarization into topic-modeling bullets.
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

## Approved Summarization Pattern

For transcript-to-bullet summarization, follow `templates/approved_summarization_embedding_pipeline.py`.

Preserve these parts unless the dataset requires a small adaptation:

- read transcript `.txt` files from a configured transcript directory,
- read metadata from a configured CSV, JSONL, or Parquet file,
- map transcripts to metadata with a stable source stem,
- use an OpenAI `responses.create` call with JSON schema output,
- request a `bullets` array,
- keep the prompt extractive and grounded in the transcript,
- remove generic channel housekeeping when it is not part of the research goal,
- save one summary record per source as JSONL,
- explode each summary into one row per bullet,
- create stable bullet IDs from source ID and bullet index,
- save the bullet dataset as Parquet.

Dependency install pattern:

```bash
pip install -qqq openai pandas pyarrow tqdm python-dotenv
```

## Reuse

See:

- `templates/common_code_patterns.md`
- `templates/prompt_design_patterns.md`
