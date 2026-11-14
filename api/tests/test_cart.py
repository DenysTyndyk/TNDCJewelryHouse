"""T2.6: cart CRUD, stock limit, ownership isolation and guest -> user merge."""
import secrets
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import select

from app.models.catalog import Category, Product, ProductVariant, VariantPrice
from app.models.commerce import Cart
from app.models.enums import CartStatus, Currency, MetalType

HEADER = "X-Cart-Session"


# —— helpers ——


def _variant(db, slug, stock=5, reserved=0, price="1000", published=True) -> int:
    """Create category + product + one priced variant; return variant id."""
    category = Category(slug=f"{slug}-cat")
    db.add(category)
    db.flush()
    product = Product(
        category_id=category.id,
        slug=slug,
        published_at=datetime.now(timezone.utc) - timedelta(minutes=5) if published else None,
    )
    db.add(product)
    db.flush()
    variant = ProductVariant(
        product_id=product.id, sku=f"{slug}-1", metal_type=MetalType.Gold, fineness=585,
        base_price=Decimal(price), stock_quantity=stock, reserved_quantity=reserved,
    )
    db.add(variant)
    db.flush()
    db.add(VariantPrice(variant_id=variant.id, currency=Currency.UAH, price=Decimal(price)))
    db.flush()
    return variant.id


def _guest():
    return {HEADER: secrets.token_urlsafe(32)}


def _add(client, headers, variant_id, quantity=1):
    return client.post("/cart/items", headers=headers, json={"variant_id": variant_id, "quantity": quantity})


def _lines(response):
    assert response.status_code == 200, response.text
    return {line["variant_id"]: line["quantity"] for line in response.json()["items"]}


# —— guest token ——


def test_guest_without_token_gets_new_token_and_empty_cart(client):
    response = client.get("/cart")

    assert response.status_code == 200
    assert response.json()["items"] == []
    assert len(response.headers[HEADER]) >= 16


def test_guest_token_is_echoed_back(client):
    headers = _guest()
    response = client.get("/cart", headers=headers)
    assert response.headers[HEADER] == headers[HEADER]


def test_too_short_token_is_rejected(client):
    assert client.get("/cart", headers={HEADER: "short"}).status_code == 422


# —— CRUD ——


def test_add_item_uses_server_price(client, db_session):
    variant_id = _variant(db_session, "t-cart-add", price="1500")

    response = _add(client, _guest(), variant_id, quantity=2)

    assert response.status_code == 200, response.text
    body = response.json()
    line = body["items"][0]
    assert line["quantity"] == 2
    assert Decimal(line["unit_price"]) == Decimal("1500")
    assert Decimal(line["unit_price_at_add"]) == Decimal("1500")
    assert Decimal(body["subtotal"]) == Decimal("3000")
    assert body["currency"] == "UAH"


def test_price_in_body_is_rejected(client, db_session):
    variant_id = _variant(db_session, "t-cart-price")
    response = client.post(
        "/cart/items", headers=_guest(), json={"variant_id": variant_id, "quantity": 1, "unit_price": "1"}
    )
    assert response.status_code == 422


def test_adding_same_variant_sums_quantity(client, db_session):
    variant_id = _variant(db_session, "t-cart-sum", stock=5)
    headers = _guest()

    _add(client, headers, variant_id, 2)
    response = _add(client, headers, variant_id, 1)

    assert _lines(response) == {variant_id: 3}


def test_update_quantity(client, db_session):
    variant_id = _variant(db_session, "t-cart-upd", stock=5)
    headers = _guest()
    item_id = _add(client, headers, variant_id, 1).json()["items"][0]["id"]

    response = client.patch(f"/cart/items/{item_id}", headers=headers, json={"quantity": 4})

    assert _lines(response) == {variant_id: 4}


def test_delete_item(client, db_session):
    variant_id = _variant(db_session, "t-cart-del")
    headers = _guest()
    item_id = _add(client, headers, variant_id).json()["items"][0]["id"]

    response = client.delete(f"/cart/items/{item_id}", headers=headers)

    assert _lines(response) == {}
    assert _lines(client.get("/cart", headers=headers)) == {}


def test_unpublished_variant_returns_404(client, db_session):
    variant_id = _variant(db_session, "t-cart-unpub", published=False)
    assert _add(client, _guest(), variant_id).status_code == 404


# —— stock limit ——


def test_add_over_free_stock_returns_409(client, db_session):
    variant_id = _variant(db_session, "t-cart-stock", stock=3, reserved=1) 

    response = _add(client, _guest(), variant_id, 3)

    assert response.status_code == 409
    assert response.json()["detail"]["available"] == 2


def test_add_where_sum_exceeds_stock_returns_409(client, db_session):
    variant_id = _variant(db_session, "t-cart-stock-sum", stock=2)
    headers = _guest()
    _add(client, headers, variant_id, 2)

    response = _add(client, headers, variant_id, 1)

    assert response.status_code == 409
    assert _lines(client.get("/cart", headers=headers)) == {variant_id: 2}  


def test_update_over_stock_returns_409(client, db_session):
    variant_id = _variant(db_session, "t-cart-stock-upd", stock=2)
    headers = _guest()
    item_id = _add(client, headers, variant_id, 1).json()["items"][0]["id"]

    response = client.patch(f"/cart/items/{item_id}", headers=headers, json={"quantity": 3})

    assert response.status_code == 409


# —— ownership ——


def test_cannot_modify_line_of_another_guest(client, db_session):
    variant_id = _variant(db_session, "t-cart-idor")
    owner = _guest()
    item_id = _add(client, owner, variant_id).json()["items"][0]["id"]
    stranger = _guest()

    assert client.patch(f"/cart/items/{item_id}", headers=stranger, json={"quantity": 2}).status_code == 404
    assert client.delete(f"/cart/items/{item_id}", headers=stranger).status_code == 404
    assert _lines(client.get("/cart", headers=owner)) == {variant_id: 1}


# —— merge on login ——


def _register_and_login(client, email, headers=None):
    password = "supersecret123"
    response = client.post(
        "/auth/register",
        json={"email": email, "password": password, "first_name": "Cart", "last_name": "Test"},
    )
    assert response.status_code == 201
    response = client.post("/auth/login", headers=headers or {}, json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _login(client, email, headers=None):
    response = client.post("/auth/login", headers=headers or {}, json={"email": email, "password": "supersecret123"})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_merge_moves_guest_lines_into_user_cart(client, db_session):
    v1 = _variant(db_session, "t-merge-1")
    v2 = _variant(db_session, "t-merge-2")
    guest = _guest()
    guest_cart_id = _add(client, guest, v1, 2).json()["id"]
    _add(client, guest, v2, 1)

    user = _register_and_login(client, "merge.move@example.com", headers=guest)

    assert _lines(client.get("/cart", headers=user)) == {v1: 2, v2: 1}
    guest_cart = db_session.scalar(select(Cart).where(Cart.id == guest_cart_id))
    assert guest_cart.status == CartStatus.Converted
    assert guest_cart.session_token is None


def test_merge_sums_quantities_capped_by_stock(client, db_session):
    variant_id = _variant(db_session, "t-merge-cap", stock=5)
    user = _register_and_login(client, "merge.cap@example.com")
    _add(client, user, variant_id, 4)
    guest = _guest()
    _add(client, guest, variant_id, 3)

    user = _login(client, "merge.cap@example.com", headers=guest)

    assert _lines(client.get("/cart", headers=user)) == {variant_id: 5}  


def test_old_guest_token_is_reusable_after_merge(client, db_session):
    variant_id = _variant(db_session, "t-merge-reuse")
    guest = _guest()
    _add(client, guest, variant_id)
    _register_and_login(client, "merge.reuse@example.com", headers=guest)

    assert _lines(client.get("/cart", headers=guest)) == {}
    assert _add(client, guest, variant_id).status_code == 200


def test_login_without_guest_token_still_works(client):
    _register_and_login(client, "merge.none@example.com")
