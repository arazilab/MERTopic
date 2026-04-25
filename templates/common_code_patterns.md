# Common Code Patterns

## 1. Environment-driven config

Use small helper functions for:

- required strings,
- optional booleans,
- optional integers,
- JSON list values.

Keep models, prompts, paths, retry counts, and seeds in `.env`.

## 2. JSONL streaming

For large corpora:

- stream the input file line by line,
- skip blank lines,
- write outputs incrementally,
- avoid loading the full corpus unless necessary.

## 3. Progress bars

Use `tqdm` for:

- row-level model calls,
- embedding batches,
- topic-labeling loops,
- parameter sweeps.

## 4. Exact-span verification

Use this sequence:

1. normalize Unicode,
2. standardize quotes and dashes,
3. compress whitespace,
4. parse bullets,
5. remove numbering and list markers,
6. verify each normalized bullet against the normalized source text.

If a span is not present verbatim after normalization, reject it.

## 5. Embedding linkage

Always store:

- source post ID,
- bullet or span ID,
- bullet index,
- embedding model,
- embedding dimensions.

This makes later topic assignments traceable.

## 6. BERTopic reproducibility

Keep these configurable:

- random seed,
- UMAP parameters,
- HDBSCAN parameters,
- stopwords,
- topic-label prompt,
- representative-example count.

Set the same seed in NumPy and UMAP.

Use a fitted BERTopic model to save the intertopic map:

```python
try:
    fig = topic_model.visualize_topics()
    fig.write_html(output_dir / "intertopic_distance_map.html")
except Exception as exc:
    print(f"Intertopic distance map generation failed: {exc}")
```

## 7. BERTopic grid metrics

For each run, save structure, representation, and separation metrics:

```python
metrics = {
    "topic_count_non_outlier": len(non_outlier_topic_ids),
    "outlier_rate": outlier_count / total_docs,
    "largest_topic_share": largest_topic_size / total_docs,
    "topic_diversity_top_10": topic_diversity(topic_terms_map, 10),
    "npmi_coherence": npmi_score,
    "u_mass_coherence": umass_score,
    "silhouette_cosine": silhouette_score(clustered_embeddings, labels, metric="cosine"),
    "davies_bouldin": davies_bouldin_score(clustered_embeddings, labels),
}
```

Interpretation:

- high coherence with too many topics can mean over-fragmentation,
- high largest-topic share can mean collapse,
- high outlier rate can mean overly strict clustering,
- low diversity can mean topic labels are redundant,
- separation metrics help test whether clusters are meaningfully distinct.

## 8. Analysis-tool export structure

A safe default is one JSON record per post with:

- `id`
- `data`
- `annotation`
- `context`
- `topic_ids`
- `topic_labels`

Where `annotation` is a list like:

- `descriptive label`
- `another descriptive label`

Use the original post as the browser unit in both modes:

- post-level topic modeling: one post, usually one topic
- bullet-level topic modeling: one post, aggregated topics from all bullets belonging to that post

## 9. Co-occurrence counting

Count co-occurrence at the post level:

- collect the unique topic IDs on a post,
- for every unordered pair, add one count,
- do not count repeated bullets from the same topic more than once for the same post.
