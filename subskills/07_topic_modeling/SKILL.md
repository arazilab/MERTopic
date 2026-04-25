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
- Keep UMAP and HDBSCAN parameters in config.
- Fix random seeds.
- Use custom stopwords when prefilter keywords would dominate topic terms.
- Save document assignments, post-level summaries, topic summaries, and an intertopic distance map.
- Save topic co-occurrence at the post level when a post can contain multiple bullet-level topics.

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

## Topic Labeling

Topic labeling should:

- use representative texts,
- avoid over-claiming a focal construct,
- return a readable sentence,
- use enough examples to stabilize labeling.

## Decision Rule

If the user does not know whether bullet or post level is preferable:

- run both,
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
TOPIC_MODEL_RANDOM_SEED=42
TOPIC_MODEL_UMAP_N_NEIGHBORS=10
TOPIC_MODEL_UMAP_N_COMPONENTS=5
TOPIC_MODEL_UMAP_MIN_DIST=0.1
TOPIC_MODEL_HDBSCAN_MIN_CLUSTER_SIZE=12
TOPIC_MODEL_HDBSCAN_MIN_SAMPLES=1
TOPIC_MODEL_INTERTOPIC_DISTANCE_HTML_FILENAME=intertopic_distance_map.html
TOPIC_MODEL_EXTRA_STOPWORDS=[]
TOPIC_LABEL_MAX_REPRESENTATIVE_DOCS=10
```

These are not universal defaults. They are an example of a defensible promoted configuration after grid search.
