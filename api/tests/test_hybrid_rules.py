from datetime import UTC, datetime, timedelta

from app.services.recommendation.hybrid import combine, novelty
from app.services.recommendation.rules import apply_rules

RANKED = [(1, 0.9), (2, 0.8), (3, 0.7), (4, 0.6), (5, 0.5)]
CATS = {1: 10, 2: 10, 3: 10, 4: 20, 5: 20}


def test_unavailable_and_purchased_are_dropped():
    out = apply_rules(RANKED, available={1, 2, 3, 4}, exclude={2}, category=CATS,
                      limit=10, max_per_category=10)
    assert [pid for pid, _ in out] == [1, 3, 4]  


def test_category_limit_is_respected():
    out = apply_rules(RANKED, available=set(CATS), exclude=set(), category=CATS,
                      limit=10, max_per_category=2)
    assert [pid for pid, _ in out] == [1, 2, 4, 5]  


def test_only_popularity_when_other_weights_zero():
    pop = {1: 0.2, 2: 1.0, 3: 0.5}
    out = combine([1, 2, 3], behavior={1: 9.0}, content={1: 1.0}, popularity=pop,
                  novelty={1: 1.0}, a=0, b=0, c=1, d=0)
    assert out == [(2, 1.0), (3, 0.5), (1, 0.2)]


def test_novelty_newest_is_one():
    now = datetime(2026, 1, 31, tzinfo=UTC)
    n = novelty({1: now, 2: now - timedelta(days=10)})
    assert n == {1: 1.0, 2: 0.0}
