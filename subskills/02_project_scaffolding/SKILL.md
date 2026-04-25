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

## Reuse

Start from:

- `config_template.env.example`
- `templates/python_stage_template.py`
- `templates/shell_runner_template.sh`
