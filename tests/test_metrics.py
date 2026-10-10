from support_agent.metrics import dedupe_docs, recall_at_k, reciprocal_rank


def test_dedupe_keeps_order():
    assert dedupe_docs(["a", "b", "a", "c"]) == ["a", "b", "c"]


def test_recall_counts_distinct_documents():
    ranked = ["a", "a", "a", "b"]
    assert recall_at_k(ranked, ["b"], k=2) == 1.0
    assert recall_at_k(ranked, ["c"], k=5) == 0.0


def test_reciprocal_rank():
    assert reciprocal_rank(["x", "y", "z"], ["z"]) == 1 / 3
    assert reciprocal_rank(["x"], ["z"]) == 0.0
