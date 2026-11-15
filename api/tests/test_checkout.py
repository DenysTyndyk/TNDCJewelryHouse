"""order_service.checkout: snapshot, reservation, free shipping, out-of-stock."""
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from app.models.catalog import Category, Product, ProductTranslation, ProductVariant, VariantPrice
from app.models.commerce import Cart, CartItem
from app.models.enums import CartStatus, Currency, DeliveryProvider, MetalType
from app.models.logistics import ShippingMethod
from app.schemas.order import CheckoutIn
from app.services import order_service

GUEST = "checkout-test-guest-token-0001"


def _setup(db, stock=3, quantity=2, price="1000.00"):
    category = Category(slug="checkout-test-rings")
    db.add(category)
    db.flush()
    product = Product(
        category_id=category.id,
        slug="checkout-test-ring",
        published_at=datetime.now(timezone.utc) - timedelta(minutes=5),
    )
    db.add(product)
    db.flush()
    db.add(ProductTranslation(product_id=product.id, locale="uk", name="Каблучка"))
    variant = ProductVariant(
        product_id=product.id, sku="CHK-R-17", size="17", metal_type=MetalType.Gold,
        fineness=585, base_price=Decimal(price), stock_quantity=stock,
    )
    db.add(variant)
    db.flush()
    db.add(VariantPrice(variant_id=variant.id, currency=Currency.UAH, price=Decimal(price)))
    method = ShippingMethod(
        provider=DeliveryProvider.NovaPoshta, name="NP", cost=Decimal("70.00"),
        currency=Currency.UAH, free_from_amount=Decimal("1500.00"),
    )
    cart = Cart(session_token=GUEST)
    db.add_all([method, cart])
    db.flush()
    db.add(CartItem(cart_id=cart.id, variant_id=variant.id, quantity=quantity,
                    unit_price_at_add=Decimal(price)))
    db.flush()
    return variant, method, cart


def _form(method_id, **overrides):
    data = {
        "recipient_name": "Олена Коваль",
        "recipient_phone": "+380501234567",
        "customer_email": "olena@example.com",
        "shipping_method_id": method_id,
        "shipping_city": "Київ",
        "provider_point_id": "12",
    }
    return CheckoutIn(**{**data, **overrides})


def test_checkout_snapshots_items_and_reserves_stock(db_session):
    variant, method, cart = _setup(db_session, stock=3, quantity=2)

    order = order_service.checkout(
        db_session, _form(method.id), user_id=None, session_token=GUEST, locale="uk"
    )

    assert order.order_number.startswith("TNDC-")
    assert order.subtotal == Decimal("2000.00")
    assert order.shipping_amount == Decimal("0.00")  
    assert order.total == Decimal("2000.00")
    [item] = order.items
    assert (item.sku, item.product_name, item.quantity, item.unit_price) == (
        "CHK-R-17", "Каблучка", 2, Decimal("1000.00"),
    )
    assert variant.reserved_quantity == 2
    assert variant.stock_quantity == 3 
    assert cart.status == CartStatus.Converted


def test_shipping_is_charged_below_free_threshold(db_session):
    _, method, _ = _setup(db_session, quantity=1, price="500.00")

    order = order_service.checkout(
        db_session, _form(method.id), user_id=None, session_token=GUEST, locale="uk"
    )

    assert order.shipping_amount == Decimal("70.00")
    assert order.total == Decimal("570.00")


def test_out_of_stock_raises_and_changes_nothing(db_session):
    variant, method, cart = _setup(db_session, stock=1, quantity=2)

    with pytest.raises(order_service.OutOfStockError) as exc:
        order_service.checkout(
            db_session, _form(method.id), user_id=None, session_token=GUEST, locale="uk"
        )

    assert exc.value.shortages == [
        {"variant_id": variant.id, "sku": "CHK-R-17", "requested": 2, "available": 1}
    ]
    assert variant.reserved_quantity == 0
    assert cart.status == CartStatus.Active


def test_nova_poshta_requires_branch(db_session):
    _, method, _ = _setup(db_session)

    with pytest.raises(order_service.DeliveryDetailsError):
        order_service.checkout(
            db_session,
            _form(method.id, provider_point_id=None, shipping_address_line="вул. Хрещатик, 1"),
            user_id=None, session_token=GUEST, locale="uk",
        )

def test_order_created_email_is_logged_in_order_language(db_session, caplog):
    _, method, _ = _setup(db_session, quantity=1, price="500.00")
    order = order_service.checkout(
        db_session, _form(method.id), user_id=None, session_token=GUEST, locale="pl"
    )

    with caplog.at_level("INFO", logger="app.email"):
        order_service.send_order_created_email(order, "pl")

    assert "to=olena@example.com" in caplog.text
    assert f"Zamówienie {order.order_number}" in caplog.text
    assert "Razem: 570.00 UAH" in caplog.text
    assert f"/orders/{order.order_number}" in caplog.text

def test_cancel_releases_reserve_and_sets_cancelled_at(db_session):
    variant, method, _ = _setup(db_session, stock=3, quantity=2)
    order = order_service.checkout(
        db_session, _form(method.id), user_id=None, session_token=GUEST, locale="uk"
    )
    assert variant.reserved_quantity == 2

    cancelled = order_service.cancel(db_session, order.order_number, user_id=None, session_token=GUEST)

    assert cancelled.status == "Cancelled"
    assert cancelled.cancelled_at is not None
    assert variant.reserved_quantity == 0
    assert variant.stock_quantity == 3


def test_cancel_twice_is_rejected(db_session):
    _, method, _ = _setup(db_session)
    order = order_service.checkout(
        db_session, _form(method.id), user_id=None, session_token=GUEST, locale="uk"
    )
    order_service.cancel(db_session, order.order_number, user_id=None, session_token=GUEST)

    with pytest.raises(order_service.InvalidTransitionError):
        order_service.cancel(db_session, order.order_number, user_id=None, session_token=GUEST)


def test_allowed_transitions_cover_every_status():
    from app.models.enums import OrderStatus
    assert set(order_service.ALLOWED_TRANSITIONS) == set(OrderStatus)
