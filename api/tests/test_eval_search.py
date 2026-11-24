from scripts.eval_search import mrr_at, ndcg_at, percentile, precision_at


def test_precision_counts_hits_in_top5():
    assert precision_at([1, 9, 2, 8, 7, 3], {1, 2, 3}) == 0.4  # 3 is 6th, outside top-5


def test_mrr_uses_first_hit_only():
    assert mrr_at([9, 8, 2, 1], {1, 2}) == 1 / 3
    assert mrr_at([9, 8], {1}) == 0.0


def test_ndcg_is_one_for_ideal_order_and_lower_otherwise():
    assert ndcg_at([1, 2, 9], {1, 2}) == 1.0
    assert 0 < ndcg_at([9, 1, 2], {1, 2}) < 1


def test_percentile_nearest_rank():
    assert percentile([10, 20, 30, 40], 0.5) == 20
    assert percentile(list(range(1, 21)), 0.95) == 19