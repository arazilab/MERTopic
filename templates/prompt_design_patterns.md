# Prompt Design Patterns

## Relevancy coding prompt

Good structure:

1. define the target construct,
2. define what counts,
3. define what does not count,
4. prohibit unsupported inference,
5. require structured output.

## Extractive summary prompt

Good structure:

1. define the goal of extraction,
2. require verbatim continuous spans,
3. prohibit paraphrase and merging,
4. specify output formatting,
5. emphasize complete coverage of distinct points.

## Retry prompt

Good structure:

1. show the rejected items,
2. explain why they failed,
3. ask for replacements only,
4. prohibit repetition of accepted items,
5. allow an empty response if nothing valid can be recovered.

## Topic-label prompt

Good structure:

1. give short dataset background,
2. give topic ID,
3. give cleaned keywords,
4. give representative texts,
5. ask for one readable sentence,
6. prohibit over-claiming a focal construct unless the texts support it.
