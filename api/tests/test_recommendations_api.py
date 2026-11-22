from app.models.enums import EventType
from tests.test_recommendation_repository import _event, _product, _variant
from app.models.catalog import Product
from app.services import order_service
from tests.test_checkout import GUEST as BUYER, _form, _setup
from tests.test_recommendation_repository import NOW

GUEST_NEW = "reco-api-guest-empty-0001"
GUEST_FAN = "reco-api-guest-fan-00001"
CONSENT = {"X-Tracking-Consent": "granted"}


def _get(client, url, token, consent=True):
    headers = {"X-Cart-Session": token, **(CONSENT if consent else {})}
    resp = client.get(url, headers=headers)
    assert resp.status_code == 200
    return resp.json()


def _fan_history(db):
    product = _product(db, "reco-api-fav")
    _variant(db, product, "RECO-API-1", "1000.00", 5)
    for _ in range(3):
        _event(db, EventType.AddToCart, product.id, 40, token=GUEST_FAN)
    db.flush()
    return product


def test_guest_without_history_gets_popularity(client):
    assert _get(client, "/recommendations/for-you", GUEST_NEW)["algorithm"] == "popularity"


def test_history_changes_the_order(client, db_session):
    fav = _fan_history(db_session)
    guest = _get(client, "/recommendations/for-you", GUEST_NEW)
    fan = _get(client, "/recommendations/for-you", GUEST_FAN)
    assert fan["algorithm"] == "hybrid"
    assert fan["items"][0]["id"] == fav.id
    assert [i["id"] for i in fan["items"]] != [i["id"] for i in guest["items"]]


def test_without_consent_history_is_ignored(client, db_session):
    _fan_history(db_session)
    assert _get(client, "/recommendations/for-you", GUEST_FAN, consent=False)["algorithm"] == "popularity"


def test_similar_excludes_itself_and_unavailable(client, db_session):
    target = _product(db_session, "reco-api-target")
    _variant(db_session, target, "RECO-API-2", "1000.00", 5)
    sold_out = _product(db_session, "reco-api-soldout")
    _variant(db_session, sold_out, "RECO-API-3", "1000.00", 0)
    db_session.flush()
    ids = [i["id"] for i in _get(client, f"/recommendations/similar/{target.id}", GUEST_NEW)["items"]]
    assert target.id not in ids
    assert sold_out.id not in ids


def test_similar_unknown_product_is_404(client):
    assert client.get("/recommendations/similar/999999999").status_code == 404

def test_similar_excludes_purchased(client, db_session):
    variant, method, _ = _setup(db_session)
    bought = db_session.get(Product, variant.product_id)
    twin = Product(category_id=bought.category_id, slug="reco-api-twin", published_at=NOW)
    db_session.add(twin)
    db_session.flush()
    _variant(db_session, twin, "RECO-API-4", "1000.00", 5)

    url = f"/recommendations/similar/{twin.id}"
    assert bought.id in [i["id"] for i in _get(client, url, BUYER)["items"]]

    order_service.checkout(db_session, _form(method.id), user_id=None, session_token=BUYER, locale="uk")
    db_session.flush()
    assert bought.id not in [i["id"] for i in _get(client, url, BUYER)["items"]]

def test_for_you_excludes_cart_items(client, db_session):
    variant, _, _ = _setup(db_session)  # puts the ring into BUYER's active cart
    ids = [i["id"] for i in _get(client, "/recommendations/for-you", BUYER)["items"]]
    assert variant.product_id not in ids
