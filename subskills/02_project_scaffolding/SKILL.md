---
name: mertopic-project-scaffolding
description: "Scaffold a reproducible MERTopic analysis project with config files, scripts, data directories, shell runners, README updates, and stage-specific output locations."
---

# Project Scaffolding

Use this sub-skill after the workflow is scoped.

## Goal

Create a project layout that is reproducible and easy to rerun.

## Create

- `.env`
- `.gitignore`
- `README.md`
- `scripts/`
- `data/raw`
- stage-specific output directories under `data/`

## Requirements

- Keep paths configurable.
- Keep prompts in config when practical.
- Keep shell runners simple and explicit.
- Update the README whenever outputs or stages change.
- Put secrets in `.env` only; never write API keys into scripts, notebooks, README files, or committed examples.
- If an API key exists in the current shell environment, use the environment variable at runtime rather than copying the secret into generated files.
- If an API key is missing, leave the `.env` value blank and stop with instructions for the user to fill it locally.
- Include a `.gitignore` entry for `.env`, raw private data, generated outputs, model artifacts, caches, and virtual environments.
- Create scripts that fail fast with a clear message when required config values or input files are missing.

## Stop Gate

After scaffolding, stop and ask the user to review `.env` and confirm:

- input paths and fields,
- enabled stages,
- prompts or construct definitions,
- model names,
- whether the agent should run API-costing stages.

Do not run relevancy coding, extraction, summarization, embeddings, or topic labeling until this confirmation is available.

## Reuse

Start from:

- `config_template.env.example`
- `templates/python_stage_template.py`
- `templates/shell_runner_template.sh`
