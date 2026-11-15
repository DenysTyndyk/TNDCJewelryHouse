"""POST/GET /orders: guest ownership by X-Cart-Session, 409 shape, cart reuse after checkout."""
from tests.test_checkout import GUEST, _form, _setup
from tests.test_cart import _register_and_login

OTHER_GUEST = "someone-else-guest-token-0002"


def _payload(method_id, **overrides):
    return _form(method_id, **overrides).model_dump(mode="json")


def test_guest_creates_and_reads_own_order(client, db_session):
    _, method, _ = _setup(db_session, stock=3, quantity=2)

    res = client.post("/orders", json=_payload(method.id), headers={"X-Cart-Session": GUEST})
    assert res.status_code == 201
    number = res.json()["order_number"]

    detail = client.get(f"/orders/{number}", headers={"X-Cart-Session": GUEST})
    assert detail.status_code == 200
    assert detail.json()["items"][0]["sku"] == "CHK-R-17"

    listing = client.get("/orders", headers={"X-Cart-Session": GUEST})
    assert [o["order_number"] for o in listing.json()] == [number]
    assert listing.json()[0]["items"] == []


def test_other_guest_gets_404_for_foreign_order(client, db_session):
    _, method, _ = _setup(db_session)
    number = client.post(
        "/orders", json=_payload(method.id), headers={"X-Cart-Session": GUEST}
    ).json()["order_number"]

    res = client.get(f"/orders/{number}", headers={"X-Cart-Session": OTHER_GUEST})
    assert res.status_code == 404
    assert client.get("/orders", headers={"X-Cart-Session": OTHER_GUEST}).json() == []


def test_out_of_stock_returns_409_with_items(client, db_session):
    variant, method, _ = _setup(db_session, stock=1, quantity=2)

    res = client.post("/orders", json=_payload(method.id), headers={"X-Cart-Session": GUEST})

    assert res.status_code == 409
    assert res.json()["detail"]["items"] == [
        {"variant_id": variant.id, "sku": "CHK-R-17", "requested": 2, "available": 1}
    ]


def test_empty_cart_returns_400(client):
    res = client.post("/orders", json=_payload(1), headers={"X-Cart-Session": OTHER_GUEST})
    assert res.status_code == 400


def test_guest_can_fill_a_new_cart_after_checkout(client, db_session):
    variant, method, _ = _setup(db_session, stock=3, quantity=2)
    client.post("/orders", json=_payload(method.id), headers={"X-Cart-Session": GUEST})

    res = client.post(
        "/cart/items", json={"variant_id": variant.id, "quantity": 1}, headers={"X-Cart-Session": GUEST}
    )
    assert res.status_code == 200
    assert res.json()["items"][0]["quantity"] == 1

def test_cancel_via_api_and_foreign_cancel_is_404(client, db_session):
    _, method, _ = _setup(db_session)
    number = client.post(
        "/orders", json=_payload(method.id), headers={"X-Cart-Session": GUEST}
    ).json()["order_number"]

    foreign = client.post(f"/orders/{number}/cancel", headers={"X-Cart-Session": OTHER_GUEST})
    assert foreign.status_code == 404

    own = client.post(f"/orders/{number}/cancel", headers={"X-Cart-Session": GUEST})
    assert own.status_code == 200
    assert own.json()["status"] == "Cancelled"

    again = client.post(f"/orders/{number}/cancel", headers={"X-Cart-Session": GUEST})
    assert again.status_code == 409

def test_logged_in_user_owns_order_guest_token_and_other_user_do_not(client, db_session):
    _setup(db_session, stock=3, quantity=1)
    method_id = client.get("/shipping-methods").json()[0]["id"]
    auth = _register_and_login(client, "orders.owner@example.com", headers={"X-Cart-Session": GUEST})

    res = client.post("/orders", json=_payload(method_id), headers=auth)
    assert res.status_code == 201, res.text
    number = res.json()["order_number"]

    assert client.get(f"/orders/{number}", headers=auth).status_code == 200
    assert [o["order_number"] for o in client.get("/orders", headers=auth).json()] == [number]

    assert client.get(f"/orders/{number}", headers={"X-Cart-Session": GUEST}).status_code == 404

    other = _register_and_login(client, "orders.other@example.com")
    assert client.get(f"/orders/{number}", headers=other).status_code == 404
    assert client.post(f"/orders/{number}/cancel", headers=other).status_code == 404
