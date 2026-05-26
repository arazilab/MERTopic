#!/usr/bin/env python3
import json
import os
from datetime import datetime, timezone
from hashlib import sha1
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from tqdm.auto import tqdm


REPO_ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = REPO_ROOT / ".env"

load_dotenv(ENV_PATH)


def get_required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def get_optional_env(name: str, default: str) -> str:
    value = os.getenv(name)
    if value is None or not value.strip():
        return default
    return value.strip()


def get_int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or not value.strip():
        return default
    return int(value.strip())


def get_float_env(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None or not value.strip():
        return default
    return float(value.strip())


def resolve_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def read_table(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".parquet":
        return pd.read_parquet(path)
    if path.suffix.lower() == ".jsonl":
        return pd.read_json(path, lines=True)
    return pd.read_csv(path)


def require_columns(dataframe: pd.DataFrame, columns: list[str]) -> None:
    missing_columns = [column for column in columns if column not in dataframe.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")


def chunk_list(values: list[str], batch_size: int):
    for start in range(0, len(values), batch_size):
        yield values[start : start + batch_size]


def default_summary_system_prompt() -> str:
    return """
You create extractive summaries for downstream topic modeling and retrieval.
Return only concrete content grounded in the source text.
Do not invent facts, merge distant ideas, or add interpretation that is not explicitly supported.
Keep the wording as close to the source as possible while making each bullet readable as a standalone statement.
""".strip()


def default_summary_user_prompt_template() -> str:
    return """
Create an extractive summary of the following transcript as concise bullet-point statements.

Requirements
- Output 6 to 12 bullets.
- Each bullet must capture a distinct idea, claim, event, recommendation, or recurring issue from the transcript.
- Stay extractive in spirit. Preserve the transcript's wording where possible and do not add outside knowledge.
- Prioritize content relevant to the user's research goal.
- Remove sponsor chatter, repetitive greetings, promo codes, requests to subscribe or comment, and other generic channel housekeeping.
- The transcript metadata is provided for context only. Do not repeat metadata in the bullets unless it is part of the substantive content.

Research goal
{research_goal}

Title
{title}

Description
{description}

Transcript
{transcript_text}
""".strip()


def build_openai_client() -> OpenAI:
    api_key = get_required_env("OPENAI_API_KEY")
    return OpenAI(api_key=api_key)


def summarize_transcript(
    client: OpenAI,
    model_name: str,
    temperature: float,
    max_output_tokens: int,
    system_prompt: str,
    user_prompt_template: str,
    research_goal: str,
    title: str,
    description: str,
    transcript_text: str,
) -> list[str]:
    prompt = user_prompt_template.format(
        research_goal=research_goal,
        title=title or "",
        description=description or "",
        transcript_text=transcript_text,
    )

    response = client.responses.create(
        model=model_name,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "extractive_summary",
                "schema": {
                    "type": "object",
                    "properties": {
                        "bullets": {
                            "type": "array",
                            "items": {"type": "string"},
                        }
                    },
                    "required": ["bullets"],
                    "additionalProperties": False,
                },
                "strict": True,
            }
        },
    )

    payload = json.loads(response.output_text)
    return [bullet.strip() for bullet in payload["bullets"] if bullet.strip()]


def run_summarization(
    client: OpenAI,
    transcript_dir: Path,
    metadata_path: Path,
    summary_output_path: Path,
) -> pd.DataFrame:
    metadata_df = read_table(metadata_path)
    source_stem_column = get_optional_env("SUMMARY_SOURCE_STEM_COLUMN", "source_stem")
    title_column = get_optional_env("SUMMARY_TITLE_COLUMN", "video_title")
    description_column = get_optional_env("SUMMARY_DESCRIPTION_COLUMN", "video_description")
    require_columns(metadata_df, [source_stem_column])

    metadata_by_stem = {row[source_stem_column]: row for _, row in metadata_df.iterrows()}
    model_name = get_optional_env("SUMMARY_MODEL", "gpt-4.1-nano")
    temperature = get_float_env("SUMMARY_TEMPERATURE", 0.0)
    max_output_tokens = get_int_env("SUMMARY_MAX_OUTPUT_TOKENS", 700)
    research_goal = get_optional_env("RESEARCH_GOAL", "")
    system_prompt = get_optional_env("SUMMARY_SYSTEM_PROMPT", default_summary_system_prompt())
    user_prompt_template = get_optional_env("SUMMARY_USER_PROMPT_TEMPLATE", default_summary_user_prompt_template())

    summary_rows = []
    transcript_paths = sorted(transcript_dir.glob("*.txt"))
    pbar = tqdm(transcript_paths, desc="Summarizing transcripts", unit="file")
    for transcript_path in pbar:
        pbar.set_description(f"Summarizing {transcript_path.stem[:40]}")
        source_stem = transcript_path.stem
        transcript_text = transcript_path.read_text(encoding="utf-8", errors="ignore").strip()
        metadata_row = metadata_by_stem.get(source_stem, {})
        metadata_dict = metadata_row.to_dict() if hasattr(metadata_row, "to_dict") else {}
        bullets = summarize_transcript(
            client=client,
            model_name=model_name,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            system_prompt=system_prompt,
            user_prompt_template=user_prompt_template,
            research_goal=research_goal,
            title=metadata_row.get(title_column, ""),
            description=metadata_row.get(description_column, ""),
            transcript_text=transcript_text,
        )

        summary_rows.append(
            {
                "source_id": sha1(source_stem.encode("utf-8")).hexdigest(),
                "source_stem": source_stem,
                "summary_bullets": bullets,
                "generated_at_utc": datetime.now(timezone.utc).isoformat(),
                **metadata_dict,
            }
        )

    summary_df = pd.DataFrame(summary_rows)
    summary_output_path.parent.mkdir(parents=True, exist_ok=True)
    summary_df.to_json(summary_output_path, orient="records", lines=True, force_ascii=False)
    return summary_df


def explode_bullets(summary_df: pd.DataFrame, bullet_output_path: Path) -> pd.DataFrame:
    source_id_column = get_optional_env("SUMMARY_SOURCE_ID_COLUMN", "source_id")
    bullet_rows = []
    pbar = tqdm(summary_df.iterrows(), total=len(summary_df), desc="Building bullet dataset", unit="source")
    for _, row in pbar:
        pbar.set_description("Building bullet dataset")
        bullets = row.get("summary_bullets") or []
        for bullet_index, bullet_text in enumerate(bullets):
            bullet_text = str(bullet_text).strip()
            if not bullet_text:
                continue

            source_id = row[source_id_column]
            metadata = row.drop(labels=["summary_bullets"]).to_dict()
            bullet_rows.append(
                {
                    **metadata,
                    "summary_bullet_id": f"{source_id}_bullet_{bullet_index:03d}",
                    "summary_bullet_index": bullet_index,
                    "summary_bullet_text": bullet_text,
                }
            )

    bullet_df = pd.DataFrame(bullet_rows)
    bullet_output_path.parent.mkdir(parents=True, exist_ok=True)
    bullet_df.to_parquet(bullet_output_path, index=False)
    return bullet_df


def create_embeddings(client: OpenAI, bullet_df: pd.DataFrame, output_path: Path, preview_path: Path) -> None:
    text_column = get_optional_env("EMBEDDING_TEXT_COLUMN", "summary_bullet_text")
    embedding_column = get_optional_env("EMBEDDING_OUTPUT_COLUMN", "summary_bullet_embedding")
    model_name = get_optional_env("EMBEDDING_MODEL", "text-embedding-3-small")
    dimensions = get_int_env("EMBEDDING_DIMENSIONS", 1536)
    batch_size = get_int_env("EMBEDDING_BATCH_SIZE", 100)
    encoding_format = get_optional_env("EMBEDDING_ENCODING_FORMAT", "float")

    require_columns(bullet_df, [text_column])
    texts = bullet_df[text_column].fillna("").astype(str).tolist()
    batches = list(chunk_list(texts, batch_size))
    embeddings = []
    pbar = tqdm(batches, desc="Creating embeddings", unit="batch")
    for batch_index, batch in enumerate(pbar, start=1):
        pbar.set_description(f"Embedding batch {batch_index}/{len(batches)}")
        response = client.embeddings.create(
            model=model_name,
            input=batch,
            dimensions=dimensions,
            encoding_format=encoding_format,
        )
        embeddings.extend(item.embedding for item in response.data)

    if len(embeddings) != len(bullet_df):
        raise ValueError("Embedding count does not match the number of bullet rows.")

    embedded_df = bullet_df.copy()
    embedded_df[embedding_column] = embeddings
    embedded_df["embedding_model"] = model_name
    embedded_df["embedding_dimensions"] = dimensions
    output_path.parent.mkdir(parents=True, exist_ok=True)
    preview_path.parent.mkdir(parents=True, exist_ok=True)
    embedded_df.to_parquet(output_path, index=False)

    preview_columns = [
        column
        for column in embedded_df.columns
        if column != embedding_column
    ]
    embedded_df[preview_columns].to_csv(preview_path, index=False)


def main() -> None:
    client = build_openai_client()
    transcript_dir = resolve_path(get_required_env("SUMMARY_TRANSCRIPT_DIR"))
    metadata_path = resolve_path(get_required_env("SUMMARY_METADATA_PATH"))
    summary_output_path = resolve_path(get_optional_env("SUMMARY_OUTPUT_JSONL_PATH", "data/summary_embeddings/bullet/extractive_summaries.jsonl"))
    bullet_output_path = resolve_path(get_optional_env("SUMMARY_BULLET_PARQUET_PATH", "data/summary_embeddings/bullet/summary_bullets.parquet"))
    embedding_output_path = resolve_path(get_optional_env("SUMMARY_BULLET_EMBEDDING_PARQUET_PATH", "data/summary_embeddings/bullet/summary_bullets_with_embeddings.parquet"))
    preview_path = resolve_path(get_optional_env("SUMMARY_BULLET_PREVIEW_PATH", "data/summary_embeddings/bullet/summary_bullets_preview.csv"))

    summary_df = run_summarization(
        client=client,
        transcript_dir=transcript_dir,
        metadata_path=metadata_path,
        summary_output_path=summary_output_path,
    )
    bullet_df = explode_bullets(summary_df, bullet_output_path)
    create_embeddings(client, bullet_df, embedding_output_path, preview_path)
    print(f"Saved summaries to {summary_output_path}")
    print(f"Saved bullet dataset to {bullet_output_path}")
    print(f"Saved embedded bullet dataset to {embedding_output_path}")
    print(f"Saved preview to {preview_path}")


if __name__ == "__main__":
    main()
