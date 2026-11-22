from datetime import UTC, datetime, timedelta

from app.models.enums import EventType as E
from app.services.recommendation.behavior import score

NOW = datetime(2026, 1, 31, tzinfo=UTC)


def test_fresh_event_outweighs_old():
    events = [(1, E.ProductView, NOW), (2, E.ProductView, NOW - timedelta(days=10))]
    s = score(events, NOW, 0.1)
    assert s[1] > s[2]


def test_purchase_outweighs_view():
    events = [(1, E.Purchase, NOW), (2, E.ProductView, NOW)]
    s = score(events, NOW, 0.1)
    assert s[1] > s[2]


def test_zero_lambda_means_no_decay():
    events = [(1, E.ProductView, NOW), (2, E.ProductView, NOW - timedelta(days=60))]
    s = score(events, NOW, 0.0)
    assert s[1] == s[2] == 1.0

