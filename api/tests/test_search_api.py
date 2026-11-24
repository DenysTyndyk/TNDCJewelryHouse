import pytest

from app.core.config import settings
from app.services.search import service as search_service
from app.services.search.embedder_client import EmbedderUnavailable
from scripts.build_embeddings import UPDATE_SEARCH_VECTOR
from tests.test_recommendation_repository import _variant
from tests.test_search_repository import _product

GUEST = "search-api-guest-0000001"


@pytest.fixture(autouse=True)
def embedder_down(monkeypatch):
    """No test may reach the real embedder; tests that need it override this."""
    def unavailable(texts, kind):
        raise EmbedderUnavailable("mocked: down")
    monkeypatch.setattr(search_service, "embed", unavailable)


def _indexed(db, slug, name, price):
    product = _product(db, slug, name, f"{name} опис")
    _variant(db, product, slug.upper(), price, 5)
    db.execute(UPDATE_SEARCH_VECTOR, {"ids": [product.id]})
    return product


def _search(client, **params):
    resp = client.get("/search", params=params, headers={"X-Cart-Session": GUEST})
    assert resp.status_code == 200, resp.text
    return resp.json()


def _ids(body):
    return [item["id"] for item in body["items"]]


def test_lexical_finds_product_by_word(client, db_session):
    product = _indexed(db_session, "search-api-word", "Каблучка Qwzword", "1000.00")
    body = _search(client, q="qwzword", mode="lexical")
    assert body["mode_used"] == "lexical"
    assert product.id in _ids(body)


def test_flag_off_forces_lexical(client, db_session, monkeypatch):
    monkeypatch.setattr(settings, "semantic_search_enabled", False)
    monkeypatch.setattr(search_service, "embed", lambda *a: pytest.fail("embedder must not be called"))
    assert _search(client, q="qwzflag", mode="hybrid")["mode_used"] == "lexical"


def test_price_filter_drops_expensive(client, db_session):
    cheap = _indexed(db_session, "search-api-cheap", "Сережки Qwzprice", "1000.00")
    pricey = _indexed(db_session, "search-api-pricey", "Сережки Qwzprice люкс", "5000.00")
    ids = _ids(_search(client, q="qwzprice", mode="lexical", price_max="2000"))
    assert cheap.id in ids
    assert pricey.id not in ids


def test_embedder_down_falls_back_with_200(client, db_session):
    product = _indexed(db_session, "search-api-down", "Підвіска Qwzdown", "1000.00")
    body = _search(client, q="qwzdown", mode="semantic")
    assert body["mode_used"] == "lexical"
    assert product.id in _ids(body)


def test_blank_query_is_422(client):
    assert client.get("/search", params={"q": "   "}).status_code == 422