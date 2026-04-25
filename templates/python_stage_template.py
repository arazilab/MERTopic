#!/usr/bin/env python3
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from tqdm import tqdm


REPO_ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = REPO_ROOT / ".env"

load_dotenv(ENV_PATH)


def get_required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def get_bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def get_int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or not value.strip():
        return default
    return int(value.strip())


def get_json_list_env(name: str):
    value = os.getenv(name, "").strip()
    if not value:
        return []
    parsed = json.loads(value)
    if not isinstance(parsed, list):
        raise ValueError(f"{name} must decode to a list")
    return parsed


def count_jsonl_rows(path: Path) -> int:
    with path.open("r", encoding="utf-8") as handle:
        return sum(1 for line in handle if line.strip())


def iter_jsonl(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def main():
    input_path = REPO_ROOT / get_required_env("INPUT_PATH")
    output_dir = REPO_ROOT / get_required_env("OUTPUT_DIR")
    output_dir.mkdir(parents=True, exist_ok=True)

    total_rows = count_jsonl_rows(input_path)
    for row in tqdm(iter_jsonl(input_path), total=total_rows, desc="Processing", unit="row"):
        _ = row
        # Add stage-specific logic here.


if __name__ == "__main__":
    main()
