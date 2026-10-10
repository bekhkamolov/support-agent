| run | gold_retrieved | gold_cited | only_gold_cited | answers_with_invented_citation | errors | prompt_tokens_mean | cached_tokens_mean | completion_tokens_mean | generation_ms_median | generation_ms_p95 | confidence |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ministral-14b-latest, k=5, cache off | 1.0 | 0.981 | 0.846 | 0.0 | 0 | 755.4 | 106.2 | 85.1 | 1470.2 | 2650.7 | {'high': 51, 'medium': 1} |
| ministral-14b-latest, k=5, cache on | 1.0 | 0.981 | 0.846 | 0.0 | 0 | 755.4 | 261.1 | 84.9 | 1739.4 | 3309.0 | {'high': 51, 'low': 1} |
