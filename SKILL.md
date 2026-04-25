---
name: mertopic
description: "Build and run MERTopic, Matt's Extraordinary, Remarkable Topic modeling technique: a config-driven text analysis workflow for keyword filtering, LLM relevancy coding, verified extractive span creation, embeddings, BERTopic topic modeling at bullet or post level, grid-search model selection, intertopic maps, co-occurrence tables, and analysis-tool exports. Use when Codex needs to create, adapt, debug, or guide an end-to-end topic modeling project over a user's text dataset."
---

# MERTopic

Use this skill when a user wants an end-to-end, configurable topic-modeling workflow over text data.

MERTopic stands for Matt's Extraordinary, Remarkable Topic modeling technique. The name has ambitions; the workflow earns them the boring way: explicit configuration, saved intermediate files, verified text units, repeatable modeling choices, and enough diagnostics to keep "the topics looked nice" from becoming the entire methods section.

This root skill is the orchestrator. It does not contain every implementation detail itself. Instead, it coordinates the subskills in `subskills/` and the reusable patterns in `templates/`.

This package is designed to be copied into another project and adapted by any coding agent that can read files, write code, run scripts, and ask the user clarifying questions.

## What This Skill Does

It helps an agent:

1. inspect a dataset,
2. clarify the research or analytic goal,
3. decide which pipeline stages are needed,
4. scaffold a config-driven project structure,
5. run or prepare the pipeline stage by stage,
6. report outputs and decision points clearly,
7. optionally justify BERTopic parameters with a grid search,
8. export outputs to external browsing and co-occurrence tools.

## Interaction Style

Be direct, skeptical, and mildly wry when it fits. Challenge weak assumptions, vague research goals, magical parameter choices, and "just run topic modeling" requests before they become expensive nonsense with CSV files attached.

Keep the humor restrained. Do not mock the user, the data, the research participants, or sensitive content. The priority is useful analysis; the dry commentary is seasoning, not the meal.

## How To Use This Package

### Non-Negotiable Operating Contract

Follow these rules before any stage-specific work:

- Inspect the user's data before proposing a pipeline.
- Ask the missing setup questions before creating scripts or running analysis.
- Do not run LDA, NMF, k-means-only clustering, or any non-BERTopic substitute unless the user explicitly asks for a different method.
- Do not run API-costing stages until the user confirms the config and provides credentials through a local `.env` file or existing environment variable.
- Do not ask the user to paste API keys into chat. Create or update `.env`, leave secrets blank when unavailable, and tell the user exactly which local variable to fill.
- Stop at major decision points when the user asked for a guided workflow. Tell the user what was created, what command to run, what output to send back, and what decision comes next.
- If the user asks for a fully automated run, still stop before the first external API call unless credentials and permission are already clearly available.

Major decision points are: post-discovery scope confirmation, after scaffolding, before LLM relevancy coding, before extraction/summarization, before embeddings, before topic modeling, before grid search, and before promoting a final model.

### 1. Start with discovery

Open:

- `subskills/01_discovery_and_scoping/SKILL.md`

Do not start by writing prompts blindly. First inspect the data and ask only the questions needed to define the workflow.

### 2. Decide which stages are needed

Choose from:

- `02_project_scaffolding`
- `03_keyword_filtering`
- `04_relevancy_coding`
- `05_span_extraction_and_verification`
- `06_embeddings`
- `07_topic_modeling`
- `08_grid_search`
- `09_analysis_tool_exports`

Each sub-skill corresponds to one pipeline stage.

### 3. Keep everything config-driven

Use:

- `config_template.env.example`

Prompts, model names, retry counts, file paths, and BERTopic parameters should live in config whenever practical.

### 4. Reuse the templates

Use the code and prompt patterns in:

- `templates/python_stage_template.py`
- `templates/shell_runner_template.sh`
- `templates/common_code_patterns.md`
- `templates/prompt_design_patterns.md`

These are meant to be adapted, not copied verbatim without thought.

## Orchestration Rules

### Ask these first-order questions

After inspecting the data, ask only the missing questions. Do not continue past discovery until the answers are clear enough to write config:

- What is the dataset and how was it collected?
- What is the unit of analysis?
- What is the substantive goal of topic modeling?
- Do you want a high-level step-by-step plan before code is written, or should the agent proceed stage by stage and stop only at decision points?
- Is keyword filtering needed?
- Is LLM relevancy coding needed?
- Should extracted spans be generic or task-specific?
- Should the final topics be modeled at bullet level, post level, or both?
- Does the user want a grid search, or only a first-pass model?
- Do they need outputs for downstream browser or co-occurrence tools?
- Should the agent run later stages directly, or create scripts/config and wait for the user to run them?

### Stage ordering

Use this order unless there is a clear reason to skip steps:

1. discovery and scoping
2. project scaffolding
3. keyword filtering
4. relevancy coding
5. span extraction and verification
6. embeddings
7. topic modeling
8. grid search
9. analysis-tool export

### Decision logic

- If the user does not want keyword filtering, skip it.
- If the user does not want LLM relevancy coding, skip it.
- If the user has not confirmed API use, scaffold but do not run LLM or embedding calls.
- If an API key is missing, write the expected `.env` variable and stop with a precise handoff.
- If the user does not provide a custom extraction goal, use a general extractive-span prompt.
- Use random seed `42` by default for reproducible stochastic stages.
- Use BERTopic `nr_topics="auto"` by default unless grid search or model selection promotes a different value.
- If topic quality is clearly poor, propose a grid search instead of ad hoc parameter tweaking.
- If the highest-coherence topic model is too fragmented for the corpus size, run a focused second-pass grid search in the middle parameter region.
- If the user needs downstream exploration, export JSON in tool-compatible annotation form.
- Save both tabular topic outputs and an intertopic distance map when topic modeling is run.

### Export convention

For external browsing and co-occurrence tools, always export one record per original post.

- If the topic model was run at the post level, annotate the original post with its assigned topic.
- If the topic model was run at the bullet level, still export the original post, but aggregate all unique topics assigned to any bullet from that post.
- The displayed text unit should always be the original title and body, not the extracted bullet alone.

## Deliverables

At minimum, produce:

- a root `.env` file,
- a `scripts/` directory,
- a `README.md`,
- saved outputs and stats at each stage,
- topic-model outputs at the requested level(s),
- optional grid-search outputs,
- external-tool export JSON when needed.

## Handoff Pattern

When stopping for the user, use this pattern:

```text
Created/updated:
- <files>

Before continuing:
1. Review <config file>.
2. Add <missing environment variables> locally.
3. Run: <exact command>
4. Send back: <specific output/stat file or error log>

Next decision:
- <what will be decided from that output>
```

Do not vaguely say "let me know when it is done" without naming the expected artifact.

## Standard Command Sequence

Adapt names and paths to the target project:

```bash
bash relevancy_coding.sh
bash summary_embedding.sh
bash post_embedding.sh
bash topic_modeling.sh
bash grid_search/run_grid_search.sh
bash grid_search/run_focused_grid_search.sh
python3 scripts/export_topic_analysis_tool_data.py --level bullet
```

If a stage is not needed, skip it explicitly and document why.

## Repeatable Topic-Selection Rationale

Use this framing when moving from exploratory outputs to a defensible final model:

- Treat BERTopic as an exploratory mixed-methods step, not automatic discovery.
- Select the final model by balancing topic count, outlier rate, largest-topic share, topic diversity, coherence, cluster separation, and qualitative inspection.
- Do not select a model by coherence alone. Very small clusters can inflate coherence while creating too many topics for interpretation.
- For bullet/span-level corpora, expect more topics than post-level corpora, but still reject models that produce a micro-cluster inventory.
- Keep high-resolution models as diagnostics when useful, and promote the model that is most interpretable for the corpus size and research question.

## Quality Bar

- Be deterministic where possible.
- Save intermediate outputs.
- Keep prompts explicit.
- Verify extracted spans against source text if the task requires exact grounding.
- Explain why each major choice was made.
- Never bury important assumptions in code only.
