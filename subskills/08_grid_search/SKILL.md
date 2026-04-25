---
name: mertopic-grid-search
description: "Run broad and focused BERTopic parameter grid searches for MERTopic, saving per-run metrics, artifacts, rankings, shortlists, and model-selection rationale beyond coherence alone."
---

# Grid Search

Use this sub-skill when BERTopic parameters need justification.

## Goal

Treat parameter selection as a reproducible model-selection problem.

## Requirements

- Put the search in its own `grid_search/` workspace.
- Keep the seed fixed.
- Define the parameter ranges before running.
- Save per-run metrics and artifacts.
- Rank runs using multiple metrics, not coherence alone.
- Preserve the broad search and focused search in separate output folders.

## Recommended Metrics

- topic count
- outlier rate
- largest-topic share
- topic diversity
- coherence
- cosine silhouette
- Davies-Bouldin score
- mean centroid cosine distance
- minimum centroid cosine distance

## Recommended Search Strategy

Start broad enough to learn which parameters matter:

```json
{
  "umap": {
    "n_neighbors": [5, 10, 15, 30],
    "n_components": [3, 5, 10],
    "min_dist": [0.0, 0.05, 0.1]
  },
  "hdbscan": {
    "min_cluster_size": [5, 10, 20, 30],
    "min_samples": [1, 5, 10]
  }
}
```

If the best-coherence run is too fragmented, run a focused search between micro-clusters and collapsed broad clusters:

```json
{
  "umap": {
    "n_neighbors": [5, 10, 15],
    "n_components": [3, 5, 10],
    "min_dist": [0.0, 0.05, 0.1]
  },
  "hdbscan": {
    "min_cluster_size": [10, 12, 15, 18],
    "min_samples": [1, 2, 3]
  }
}
```

For each run, save:

```text
grid_search/results/run_metrics.csv
grid_search/results/run_ranking.csv
grid_search/results/runs/<run_id>/params.json
grid_search/results/runs/<run_id>/metrics.json
grid_search/results/runs/<run_id>/topic_summary.csv
grid_search/results/runs/<run_id>/document_topics_preview.csv
```

For focused searches, also write a shortlist:

```text
grid_search/focused_results/focused_candidate_shortlist.csv
```

## Selection Rule

Use explicit filters before ranking:

- reject too few topics,
- reject too many topics for the corpus size,
- reject high largest-topic share,
- reject excessive outlier rate,
- reject low diversity,
- reject models whose topic summaries are not interpretable.

Then compare the remaining runs. Prefer a model that:

- has enough topics to capture distinct phenomena,
- has no dominant topic,
- has acceptable outlier rate,
- has good but not necessarily maximal coherence,
- has strong diversity,
- has reasonable separation metrics,
- can be explained in the methods section.

## Output

The user should be able to answer:

- which runs are best,
- why they are best,
- what parameter regions matter,
- which settings should be promoted into the main pipeline.

## Promotion Step

After selecting a run, copy its parameters into the main config, rerun topic modeling, then rerun the analysis export:

```bash
bash topic_modeling.sh
python3 scripts/export_topic_analysis_tool_data.py --level bullet
```
