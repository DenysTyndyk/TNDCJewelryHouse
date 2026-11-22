from datetime import UTC, datetime, timedelta
from tests.test_catalog_api import _category, _product, _slugs
from app.services.recommendation.popularity import score 


NOW = datetime(2026, 1, 31, tzinfo=UTC)
OLD = NOW - timedelta(days=100)


def test_more_events_rank_higher():
    s = score([(1, 10, 20), (2, 2, 5)], {1: OLD, 2: OLD}, NOW, 7, 30)
    assert s[1] > s[2]
    assert s[1] == 1.0  


def test_younger_product_with_same_count_ranks_higher():
    young = NOW - timedelta(days=3)
    s = score([(1, 6, 6), (2, 6, 6)], {1: young, 2: OLD}, NOW, 7, 30)
    assert s[1] > s[2]


def test_unpublished_product_is_skipped():
    assert score([(99, 5, 5)], {}, NOW, 7, 30) == {}

def test_inactive_category_hides_its_products(client, db_session):
    category = _category(db_session, "t-hidden")
    _product(db_session, category, "t-hidden-ring")
    category.is_active = False
    db_session.flush()

    assert _slugs(client.get("/products?category=t-hidden")) == []
    assert client.get("/products/t-hidden-ring").status_code == 404
