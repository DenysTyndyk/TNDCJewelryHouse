"""M8: click tracking contract, history sections, personal catalog order, header suggestions."""

from app.models.catalog import ProductTranslation
from app.models.enums import EventType
from tests.test_events import GUEST_HEADERS
from tests.test_recommendation_repository import _event, _product, _variant
from tests.test_recommendations_api import GUEST_FAN, _fan_history, _get

VIEWER = "reco-m8-viewer-000000001"


def _viewed(db, slug):
    product = _product(db, slug)
    _variant(db, product, slug.upper(), "1000.00", 5)
    return product


def test_click_recommendation_requires_algorithm(client, db_session):
    product = _viewed(db_session, "reco-m8-click")
    db_session.flush()

    def post(event):
        return client.post("/events", headers=GUEST_HEADERS, json={"events": [event]}).status_code

    assert post({"event_type": "ClickRecommendation", "product_id": product.id}) == 422
    assert post({"event_type": "ClickRecommendation", "product_id": product.id, "source": "hybrid"}) == 204


def test_recently_viewed_newest_first_and_needs_consent(client, db_session):
    older, newer = _viewed(db_session, "reco-m8-older"), _viewed(db_session, "reco-m8-newer")
    _event(db_session, EventType.ProductView, older.id, 2, token=VIEWER)
    _event(db_session, EventType.ProductView, newer.id, 1, token=VIEWER)
    _event(db_session, EventType.ProductView, older.id, 3, token=VIEWER)  # repeat view: listed once
    db_session.flush()

    body = _get(client, "/recommendations/recently-viewed", VIEWER)
    assert body["algorithm"] == "history"
    assert [i["id"] for i in body["items"]] == [newer.id, older.id]
    assert _get(client, "/recommendations/recently-viewed", VIEWER, consent=False)["items"] == []


def test_also_viewed_ranks_by_distinct_viewers(client, db_session):
    anchor = _viewed(db_session, "reco-m8-anchor")
    popular, rare = _viewed(db_session, "reco-m8-popular"), _viewed(db_session, "reco-m8-rare")
    for i in range(2):
        token = f"reco-m8-co-viewer-{i:07d}"
        _event(db_session, EventType.ProductView, anchor.id, 1, token=token)
        _event(db_session, EventType.ProductView, popular.id, 1, token=token)
    one = "reco-m8-co-viewer-rare001"
    _event(db_session, EventType.ProductView, anchor.id, 1, token=one)
    for _ in range(5):  # many views by one person must not beat two different people
        _event(db_session, EventType.ProductView, rare.id, 1, token=one)
    db_session.flush()

    body = _get(client, f"/recommendations/also-viewed/{anchor.id}", VIEWER)
    assert body["algorithm"] == "co_view"
    assert [i["id"] for i in body["items"]][:2] == [popular.id, rare.id]


def test_catalog_recommended_sort_is_personal_and_paginates(client, db_session):
    fav = _fan_history(db_session)
    first = _get(client, "/products?sort=recommended&limit=1", GUEST_FAN)
    assert first["items"][0]["id"] == fav.id
    second = _get(client, f"/products?sort=recommended&limit=1&cursor={first['next_cursor']}", GUEST_FAN)
    assert second["items"][0]["id"] != fav.id


def test_suggest_matches_name_case_insensitive_and_escapes_wildcards(client, db_session):
    product = _viewed(db_session, "reco-m8-suggest")
    db_session.add(ProductTranslation(product_id=product.id, locale="uk", name="Каблучка Конюшина М8"))
    db_session.flush()

    hits = client.get("/search/suggest", params={"q": "конюшина м8", "locale": "uk"}).json()
    assert {"slug": "reco-m8-suggest", "name": "Каблучка Конюшина М8"} in hits
    assert client.get("/search/suggest", params={"q": "%_", "locale": "uk"}).json() == []
    assert client.get("/search/suggest", params={"q": "a"}).status_code == 422
