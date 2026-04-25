---
name: mertopic-keyword-filtering
description: "Create recall-oriented keyword filtering for a MERTopic corpus using boundary-aware regex patterns, match statistics, filtered outputs, and transparent reporting of broad or noisy terms."
---

# Keyword Filtering

Use this sub-skill when the user wants a recall-oriented candidate set before LLM coding.

## Goal

Reduce the corpus to likely-relevant cases without relying on plain substring matching.

## Rules

- Use boundary-aware regexes.
- Add small morphological variants when useful.
- Avoid false positives from substring overlap.
- Save both filtered rows and stats.

## Report

Always report:

- input size,
- matched size,
- match rate,
- top matched terms,
- any known broad or noisy terms.

## Reuse

See `templates/common_code_patterns.md` for:

- regex pattern structure,
- JSONL streaming pattern,
- stats file pattern.
