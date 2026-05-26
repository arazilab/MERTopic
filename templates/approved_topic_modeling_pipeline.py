#!/usr/bin/env python3
import json
import os
import random
from collections import Counter
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
from bertopic import BERTopic
from dotenv import load_dotenv
from hdbscan import HDBSCAN
from openai import OpenAI
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from tqdm.auto import tqdm
from umap import UMAP


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


def get_json_list_env(name: str):
    value = os.getenv(name, "").strip()
    if not value:
        return []
    parsed = json.loads(value)
    if not isinstance(parsed, list):
        raise ValueError(f"{name} must decode to a list")
    return parsed


def resolve_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def parse_nr_topics(value: str):
    normalized = value.strip().lower()
    if normalized == "auto":
        return "auto"
    return int(value)


def to_embedding_array(value):
    if isinstance(value, np.ndarray):
        return value.astype(np.float32)
    return np.asarray(value, dtype=np.float32)


def require_columns(dataframe: pd.DataFrame, columns: list[str]) -> None:
    missing_columns = [column for column in columns if column not in dataframe.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")


def cleaned_topic_terms(topic_model, topic_id: int, stopwords: set[str], max_terms: int = 8) -> list[str]:
    if topic_id == -1:
        return ["outlier"]

    seen = set()
    cleaned_terms = []
    for term, _weight in topic_model.get_topic(topic_id) or []:
        normalized = term.strip().lower()
        if not normalized or normalized in stopwords or normalized in seen:
            continue
        seen.add(normalized)
        cleaned_terms.append(normalized)
        if len(cleaned_terms) >= max_terms:
            break

    return cleaned_terms or [f"topic_{topic_id}"]


def fallback_topic_label(topic_id: int, topic_terms: list[str]) -> str:
    if topic_id == -1:
        return "Outlier / Mixed"
    return " / ".join(topic_terms[:4])


def normalize_representative_doc(text: str, max_chars: int) -> str:
    normalized = " ".join(str(text).split())
    if len(normalized) <= max_chars:
        return normalized
    return normalized[: max_chars - 3].rstrip() + "..."


def build_dataset_background(dataframe: pd.DataFrame, id_column: str, context_columns: list[str]) -> str:
    unique_items = dataframe[id_column].dropna().nunique()
    context_bits = []
    for column in context_columns:
        if column in dataframe.columns:
            sample_value = dataframe[column].dropna().astype(str).head(1)
            if not sample_value.empty:
                context_bits.append(f"{column} example, {sample_value.iloc[0][:160]}")

    context_text = "; ".join(context_bits) if context_bits else "No extra context columns were configured."
    return (
        f"This dataset contains {len(dataframe):,} rows across {unique_items:,} source items. "
        f"{context_text}"
    )


def build_topic_label_prompt(
    topic_id: int,
    topic_terms: list[str],
    representative_docs: list[str],
    dataset_background: str,
    max_doc_chars: int,
) -> str:
    representative_section = "\n".join(
        f"- {normalize_representative_doc(doc, max_doc_chars)}" for doc in representative_docs
    ) or "- No representative documents were available."

    return f"""
You are labeling a topic discovered in a BERTopic model.

Dataset background
{dataset_background}

Topic ID
{topic_id}

Top topic keywords
{', '.join(topic_terms)}

Representative texts
{representative_section}

Return only a concise topic name in 2 to 6 words.
Do not include quotation marks, numbering, or any explanation.
""".strip()


def build_openai_client():
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return None
    return OpenAI(api_key=api_key)


def gpt_topic_label(
    topic_id: int,
    topic_terms: list[str],
    representative_docs: list[str],
    dataset_background: str,
    client,
    model_name: str,
    max_doc_chars: int,
    max_output_tokens: int,
) -> str:
    fallback_label = fallback_topic_label(topic_id, topic_terms)
    if topic_id == -1 or client is None:
        return fallback_label

    prompt = build_topic_label_prompt(
        topic_id=topic_id,
        topic_terms=topic_terms,
        representative_docs=representative_docs,
        dataset_background=dataset_background,
        max_doc_chars=max_doc_chars,
    )

    try:
        response = client.responses.create(
            model=model_name,
            input=prompt,
            max_output_tokens=max_output_tokens,
        )
        label = response.output_text.strip()
        return label or fallback_label
    except Exception as exc:
        print(f"GPT labeling failed for topic {topic_id}: {exc}")
        return fallback_label


def unique_modeled_topics(values) -> list[int]:
    return sorted({int(value) for value in values if int(value) != -1})


def topic_labels_without_outlier(values) -> list[str]:
    return sorted({str(value) for value in values if str(value) != "Outlier / Mixed"})


def save_intertopic_map(topic_model, output_path: Path) -> None:
    try:
        fig = topic_model.visualize_topics()
        fig.write_html(output_path)
    except Exception as exc:
        print(f"Intertopic distance map generation failed: {exc}")


def save_cooccurrence_network(
    cooccurrence_df: pd.DataFrame,
    topic_label_map: dict[int, str],
    output_path: Path,
    random_seed: int,
) -> None:
    if cooccurrence_df.empty:
        output_path.write_text("<html><body><p>No topic co-occurrence pairs were found.</p></body></html>")
        return

    graph = nx.Graph()
    for topic_id, label in topic_label_map.items():
        if topic_id != -1:
            graph.add_node(topic_id, label=label)

    for row in cooccurrence_df.itertuples(index=False):
        graph.add_edge(
            int(row.topic_a),
            int(row.topic_b),
            weight=int(row.shared_source_count),
        )

    positions = nx.spring_layout(graph, seed=random_seed, weight="weight")
    edge_x = []
    edge_y = []
    for left_topic, right_topic in graph.edges():
        left_x, left_y = positions[left_topic]
        right_x, right_y = positions[right_topic]
        edge_x.extend([left_x, right_x, None])
        edge_y.extend([left_y, right_y, None])

    node_x = []
    node_y = []
    node_text = []
    node_sizes = []
    for topic_id in graph.nodes():
        x_value, y_value = positions[topic_id]
        node_x.append(x_value)
        node_y.append(y_value)
        node_text.append(f"{topic_id}, {graph.nodes[topic_id]['label']}")
        node_sizes.append(10 + 2 * graph.degree(topic_id))

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=edge_x,
            y=edge_y,
            mode="lines",
            line=dict(width=1, color="#888"),
            hoverinfo="none",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            text=node_text,
            textposition="top center",
            marker=dict(size=node_sizes, color="#2f6f9f"),
            hoverinfo="text",
        )
    )
    fig.update_layout(
        title="Topic co-occurrence network",
        showlegend=False,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        margin=dict(l=20, r=20, t=50, b=20),
    )
    fig.write_html(output_path)


def main() -> None:
    input_path = resolve_path(get_required_env("TOPIC_MODEL_INPUT_PATH"))
    output_dir = resolve_path(get_required_env("TOPIC_MODEL_OUTPUT_DIR"))
    output_dir.mkdir(parents=True, exist_ok=True)

    id_column = get_optional_env("TOPIC_MODEL_SOURCE_ID_COLUMN", "source_id")
    text_column = get_optional_env("TOPIC_MODEL_TEXT_COLUMN", "text")
    embedding_column = get_optional_env("TOPIC_MODEL_EMBEDDING_COLUMN", "embedding")
    unit_id_column = get_optional_env("TOPIC_MODEL_UNIT_ID_COLUMN", "unit_id")
    unit_index_column = get_optional_env("TOPIC_MODEL_UNIT_INDEX_COLUMN", "unit_index")
    context_columns = get_json_list_env("TOPIC_MODEL_CONTEXT_COLUMNS_JSON")

    random_seed = get_int_env("TOPIC_MODEL_RANDOM_SEED", 42)
    nr_topics = parse_nr_topics(get_optional_env("TOPIC_MODEL_BERTOPIC_NR_TOPICS", "auto"))

    random.seed(random_seed)
    np.random.seed(random_seed)

    dataframe = pd.read_parquet(input_path)
    required_columns = [id_column, text_column, embedding_column]
    optional_trace_columns = [unit_id_column, unit_index_column]
    require_columns(dataframe, required_columns)
    print(f"Loaded {len(dataframe):,} rows from {input_path}")

    texts = dataframe[text_column].fillna("").astype(str).tolist()
    embedding_rows = []
    pbar = tqdm(dataframe[embedding_column], desc="Loading embeddings", unit="row")
    for value in pbar:
        pbar.set_description("Loading embeddings")
        embedding_rows.append(to_embedding_array(value))

    embeddings = np.vstack(embedding_rows)
    print(f"Text count: {len(texts):,}")
    print(f"Embedding matrix shape: {embeddings.shape}")

    umap_model = UMAP(
        n_neighbors=get_int_env("TOPIC_MODEL_UMAP_N_NEIGHBORS", 10),
        n_components=get_int_env("TOPIC_MODEL_UMAP_N_COMPONENTS", 5),
        min_dist=get_float_env("TOPIC_MODEL_UMAP_MIN_DIST", 0.1),
        random_state=random_seed,
        transform_seed=random_seed,
    )
    hdbscan_model = HDBSCAN(
        min_cluster_size=get_int_env("TOPIC_MODEL_HDBSCAN_MIN_CLUSTER_SIZE", 12),
        min_samples=get_int_env("TOPIC_MODEL_HDBSCAN_MIN_SAMPLES", 1),
        prediction_data=True,
    )
    topic_model = BERTopic(
        nr_topics=nr_topics,
        verbose=True,
        umap_model=umap_model,
        hdbscan_model=hdbscan_model,
    )

    topics, probabilities = topic_model.fit_transform(texts, embeddings)
    non_outlier_count = len(set(topics)) - (1 if -1 in topics else 0)
    print(f"Model fit complete. Found {non_outlier_count:,} non-outlier topics.")

    stopwords = set(ENGLISH_STOP_WORDS)
    stopwords.update(get_json_list_env("TOPIC_MODEL_EXTRA_STOPWORDS"))
    unique_topics = sorted(set(int(topic) for topic in topics))
    topic_terms_map = {
        topic_id: cleaned_topic_terms(topic_model, topic_id, stopwords)
        for topic_id in unique_topics
    }

    dataset_background = build_dataset_background(dataframe, id_column, context_columns)
    openai_client = build_openai_client()
    labeling_model = get_optional_env("TOPIC_LABELING_MODEL", "gpt-4.1-nano")
    max_docs = get_int_env("TOPIC_LABEL_MAX_REPRESENTATIVE_DOCS", 5)
    max_doc_chars = get_int_env("TOPIC_LABEL_MAX_DOC_CHARS", 280)
    max_output_tokens = get_int_env("TOPIC_LABEL_MAX_OUTPUT_TOKENS", 100)

    topic_label_map = {}
    pbar = tqdm(unique_topics, desc="Generating topic labels", unit="topic")
    for topic_id in pbar:
        pbar.set_description(f"Labeling topic {topic_id}")
        representative_docs = topic_model.get_representative_docs(topic_id) or []
        topic_label_map[topic_id] = gpt_topic_label(
            topic_id=topic_id,
            topic_terms=topic_terms_map[topic_id],
            representative_docs=representative_docs[:max_docs],
            dataset_background=dataset_background,
            client=openai_client,
            model_name=labeling_model,
            max_doc_chars=max_doc_chars,
            max_output_tokens=max_output_tokens,
        )

    document_topics_df = dataframe.copy()
    document_topics_df["topic"] = topics
    document_topics_df["topic_probability"] = [None] * len(topics) if probabilities is None else probabilities
    document_topics_df["topic_label"] = document_topics_df["topic"].map(topic_label_map)
    document_topics_df["topic_terms"] = document_topics_df["topic"].map(
        lambda topic_id: ", ".join(topic_terms_map[int(topic_id)])
    )
    document_topics_df.to_csv(output_dir / get_optional_env("TOPIC_MODEL_DOCUMENT_TOPICS_FILENAME", "document_topics.csv"), index=False)

    topic_summary_df = (
        document_topics_df.groupby("topic", dropna=False)
        .agg(
            document_count=(text_column, "count"),
            source_count=(id_column, lambda values: values.dropna().nunique()),
        )
        .reset_index()
    )
    topic_summary_df["topic_label"] = topic_summary_df["topic"].map(topic_label_map)
    topic_summary_df["topic_terms"] = topic_summary_df["topic"].map(
        lambda topic_id: ", ".join(topic_terms_map[int(topic_id)])
    )
    topic_summary_df = topic_summary_df.sort_values(
        ["document_count", "source_count"], ascending=[False, False]
    ).reset_index(drop=True)
    topic_summary_df.to_csv(output_dir / get_optional_env("TOPIC_MODEL_TOPIC_SUMMARY_FILENAME", "topic_summary.csv"), index=False)

    group_columns = [id_column] + [column for column in context_columns if column in document_topics_df.columns]
    aggregations = {
        "topic_ids": ("topic", unique_modeled_topics),
        "topic_labels": ("topic_label", topic_labels_without_outlier),
        "document_count": (text_column, "count"),
        "unique_topic_count": ("topic", lambda values: len({int(value) for value in values if int(value) != -1})),
        "outlier_document_count": ("topic", lambda values: sum(int(value) == -1 for value in values)),
    }
    for column in optional_trace_columns:
        if column in document_topics_df.columns:
            aggregations[f"{column}_count"] = (column, "count")

    post_topics_df = document_topics_df.groupby(group_columns, dropna=False).agg(**aggregations).reset_index()
    post_topics_df.to_csv(output_dir / get_optional_env("TOPIC_MODEL_POST_TOPICS_FILENAME", "post_topics.csv"), index=False)

    cooccurrence_counter = Counter()
    pbar = tqdm(post_topics_df["topic_ids"], desc="Counting co-occurrence", unit="source")
    for topic_ids in pbar:
        pbar.set_description("Counting co-occurrence")
        for left_topic, right_topic in combinations(sorted(set(topic_ids)), 2):
            cooccurrence_counter[(left_topic, right_topic)] += 1

    cooccurrence_rows = []
    for (left_topic, right_topic), shared_source_count in cooccurrence_counter.items():
        cooccurrence_rows.append(
            {
                "topic_a": left_topic,
                "topic_a_label": topic_label_map[left_topic],
                "topic_b": right_topic,
                "topic_b_label": topic_label_map[right_topic],
                "shared_source_count": shared_source_count,
            }
        )

    if cooccurrence_rows:
        topic_cooccurrence_df = pd.DataFrame(cooccurrence_rows).sort_values(
            "shared_source_count", ascending=False
        ).reset_index(drop=True)
    else:
        topic_cooccurrence_df = pd.DataFrame(
            columns=["topic_a", "topic_a_label", "topic_b", "topic_b_label", "shared_source_count"]
        )
    topic_cooccurrence_df.to_csv(
        output_dir / get_optional_env("TOPIC_MODEL_TOPIC_COOCCURRENCE_FILENAME", "topic_cooccurrence.csv"),
        index=False,
    )
    save_cooccurrence_network(
        topic_cooccurrence_df,
        topic_label_map,
        output_dir / get_optional_env("TOPIC_MODEL_TOPIC_COOCCURRENCE_HTML_FILENAME", "topic_cooccurrence_network.html"),
        random_seed,
    )

    save_intertopic_map(
        topic_model,
        output_dir / get_optional_env("TOPIC_MODEL_INTERTOPIC_DISTANCE_HTML_FILENAME", "intertopic_distance_map.html"),
    )

    output_index_df = pd.DataFrame(
        [
            {"file": get_optional_env("TOPIC_MODEL_DOCUMENT_TOPICS_FILENAME", "document_topics.csv"), "description": "Document-level topic assignments"},
            {"file": get_optional_env("TOPIC_MODEL_POST_TOPICS_FILENAME", "post_topics.csv"), "description": "Source-level topic summaries"},
            {"file": get_optional_env("TOPIC_MODEL_TOPIC_SUMMARY_FILENAME", "topic_summary.csv"), "description": "Topic summary with document and source counts"},
            {"file": get_optional_env("TOPIC_MODEL_TOPIC_COOCCURRENCE_FILENAME", "topic_cooccurrence.csv"), "description": "Topic co-occurrence counts across sources"},
            {"file": get_optional_env("TOPIC_MODEL_TOPIC_COOCCURRENCE_HTML_FILENAME", "topic_cooccurrence_network.html"), "description": "Topic co-occurrence network"},
            {"file": get_optional_env("TOPIC_MODEL_INTERTOPIC_DISTANCE_HTML_FILENAME", "intertopic_distance_map.html"), "description": "BERTopic intertopic distance map"},
        ]
    )
    output_index_df.to_csv(output_dir / "output_index.csv", index=False)
    print(output_index_df)


if __name__ == "__main__":
    main()
