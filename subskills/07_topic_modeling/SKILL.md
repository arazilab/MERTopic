---
name: mertopic-topic-modeling
description: "Run BERTopic for MERTopic using saved embeddings, configurable UMAP/HDBSCAN settings, reproducible seeds, topic summaries, labels, co-occurrence tables, and intertopic maps."
---

# Topic Modeling

Use this sub-skill to run BERTopic over saved embeddings.

## Goal

Produce interpretable topic outputs at bullet level, post level, or both.

## Requirements

- Reuse stored embeddings.
- Use `templates/approved_topic_modeling_pipeline.py` as the default code sample for this stage.
- Keep UMAP and HDBSCAN parameters in config.
- Fix random seeds to `42` by default across NumPy, UMAP, and any other stochastic component that exposes a seed.
- Use custom stopwords when prefilter keywords would dominate topic terms.
- Save document assignments, post-level summaries, topic summaries, and an intertopic distance map.
- Save topic co-occurrence at the post level when a post can contain multiple bullet-level topics.
- Use BERTopic unless the user explicitly requests a different algorithm.
- Set BERTopic `nr_topics="auto"` by default, exposed in config as `TOPIC_MODEL_BERTOPIC_NR_TOPICS=auto`.
- Do not silently substitute LDA, NMF, k-means-only clustering, or a local toy model because BERTopic dependencies are unavailable.
- If BERTopic or dependencies are missing, install them with approval or stop with exact installation instructions.
- Inspect the embedding file before modeling and confirm it contains the expected text, IDs, and embedding vectors.

Dependency install pattern:

```bash
pip install -qqq bertopic umap-learn hdbscan scikit-learn pandas pyarrow numpy tqdm plotly networkx openai python-dotenv
```

## Standard Outputs

For each modeled level, write:

- `document_topics.csv`
- `post_topics.csv`
- `topic_summary.csv`
- `topic_cooccurrence.csv`
- `topic_cooccurrence_network.html`
- `intertopic_distance_map.html`

The intertopic distance map can usually be generated from a fitted BERTopic model with:

```python
fig = topic_model.visualize_topics()
fig.write_html(output_dir / "intertopic_distance_map.html")
```

## Approved Code Pattern

The topic modeling script should follow the pattern in `templates/approved_topic_modeling_pipeline.py`.

Preserve these parts unless there is a clear dataset reason to adapt them:

- read the embedded Parquet file with pandas,
- validate the source ID, text, and embedding columns before fitting,
- convert stored embeddings to a `float32` NumPy matrix with a `tqdm` progress bar,
- set `random.seed`, `np.random.seed`, UMAP `random_state`, and UMAP `transform_seed`,
- pass the stored embeddings into `topic_model.fit_transform(texts, embeddings)`,
- use `HDBSCAN(prediction_data=True)`,
- use BERTopic `nr_topics` from config, defaulting to `auto`,
- build readable fallback labels from cleaned topic terms,
- use OpenAI labels only when `OPENAI_API_KEY` is available,
- save document topics, source-level topics, topic summary, topic co-occurrence, output index, and intertopic map.
- save the co-occurrence network HTML with a deterministic layout seed when co-occurrence is requested.

The approved notebook used bullet rows from videos. In other projects, map those fields through config instead of hard-coding names.
Use source-level grouping for co-occurrence. For example, group bullet topics by original post, video, interview, comment thread, or document.

## Topic Labeling

Topic labeling should:

- use representative texts,
- avoid over-claiming a focal construct,
- return a readable sentence,
- use enough examples to stabilize labeling.

## Decision Rule

If the user does not know whether bullet or post level is preferable:

- propose running both,
- compare interpretability and collapse,
- recommend one.

If bullet-level modeling creates too many tiny topics:

- do not assume the highest-coherence model is best,
- inspect topic count relative to document count,
- check whether the intertopic map shows many nearby clusters,
- run a focused grid search with larger `min_cluster_size` values,
- choose the model that balances coherence with interpretability.

## Config Pattern

Keep these values in the project config:

```bash
TOPIC_MODEL_INPUT_PATH=data/summary_embeddings/bullet/summary_bullets_with_embeddings.parquet
TOPIC_MODEL_OUTPUT_DIR=data/topic_modeling/bullet
TOPIC_MODEL_SOURCE_ID_COLUMN=source_id
TOPIC_MODEL_TEXT_COLUMN=text
TOPIC_MODEL_EMBEDDING_COLUMN=embedding
TOPIC_MODEL_UNIT_ID_COLUMN=unit_id
TOPIC_MODEL_UNIT_INDEX_COLUMN=unit_index
TOPIC_MODEL_CONTEXT_COLUMNS_JSON=[]
TOPIC_MODEL_RANDOM_SEED=42
TOPIC_MODEL_UMAP_N_NEIGHBORS=10
TOPIC_MODEL_UMAP_N_COMPONENTS=5
TOPIC_MODEL_UMAP_MIN_DIST=0.1
TOPIC_MODEL_HDBSCAN_MIN_CLUSTER_SIZE=12
TOPIC_MODEL_HDBSCAN_MIN_SAMPLES=1
TOPIC_MODEL_BERTOPIC_NR_TOPICS=auto
TOPIC_MODEL_DOCUMENT_TOPICS_FILENAME=document_topics.csv
TOPIC_MODEL_POST_TOPICS_FILENAME=post_topics.csv
TOPIC_MODEL_TOPIC_SUMMARY_FILENAME=topic_summary.csv
TOPIC_MODEL_TOPIC_COOCCURRENCE_FILENAME=topic_cooccurrence.csv
TOPIC_MODEL_TOPIC_COOCCURRENCE_HTML_FILENAME=topic_cooccurrence_network.html
TOPIC_MODEL_INTERTOPIC_DISTANCE_HTML_FILENAME=intertopic_distance_map.html
TOPIC_MODEL_EXTRA_STOPWORDS=[]
TOPIC_LABEL_MAX_REPRESENTATIVE_DOCS=10
```

These are not universal defaults. They are an example of a defensible promoted configuration after grid search.
