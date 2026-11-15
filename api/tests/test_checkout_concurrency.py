
import threading
import time
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest
from sqlalchemy import delete, select, text

from app.db.session import SessionLocal
from app.models.catalog import Category, Product, ProductVariant, VariantPrice
from app.models.commerce import Cart, CartItem, Order, OrderItem
from app.models.enums import Currency, DeliveryProvider, MetalType
from app.models.logistics import ShippingMethod
from app.services import order_service
from tests.test_checkout import _form

HOLD_SECONDS = 1.0


@pytest.fixture()
def last_unit():
    """A variant with stock 1 in two guest carts. Everything is deleted afterwards."""
    suffix = uuid.uuid4().hex[:8]
    tokens = [f"race-a-{suffix}-token", f"race-b-{suffix}-token"]

    with SessionLocal() as s:
        category = Category(slug=f"race-{suffix}")
        s.add(category)
        s.flush()
        product = Product(
            category_id=category.id,
            slug=f"race-ring-{suffix}",
            published_at=datetime.now(timezone.utc) - timedelta(minutes=5),
        )
        s.add(product)
        s.flush()
        variant = ProductVariant(
            product_id=product.id, sku=f"RACE-{suffix}", metal_type=MetalType.Gold,
            fineness=585, base_price=Decimal("1000.00"), stock_quantity=1,
        )
        s.add(variant)
        s.flush()
        s.add(VariantPrice(variant_id=variant.id, currency=Currency.UAH, price=Decimal("1000.00")))
        method = ShippingMethod(
            provider=DeliveryProvider.NovaPoshta, name="NP", cost=Decimal("70.00"), currency=Currency.UAH,
        )
        carts = [Cart(session_token=t) for t in tokens]
        s.add(method)
        s.add_all(carts)
        s.flush()
        s.add_all([
            CartItem(cart_id=c.id, variant_id=variant.id, quantity=1, unit_price_at_add=Decimal("1000.00"))
            for c in carts
        ])
        s.commit()
        ids = {
            "category": category.id,
            "product": product.id,
            "variant": variant.id,
            "method": method.id,
            "carts": [c.id for c in carts],
        }

    yield ids, tokens

    with SessionLocal() as s:
        order_ids = select(Order.id).where(Order.session_token.in_(tokens))
        s.execute(delete(OrderItem).where(OrderItem.order_id.in_(order_ids)))
        s.execute(delete(Order).where(Order.session_token.in_(tokens)))
        s.execute(delete(Cart).where(Cart.id.in_(ids["carts"])))  # cart_items cascade
        s.execute(delete(Product).where(Product.id == ids["product"]))  # variants, prices cascade
        s.execute(delete(Category).where(Category.id == ids["category"]))
        s.execute(delete(ShippingMethod).where(ShippingMethod.id == ids["method"]))
        s.commit()


def test_only_one_buyer_gets_the_last_unit(last_unit):
    ids, (token_a, token_b) = last_unit
    a_holds_lock = threading.Event()
    results = {}

    def buyer_a():
        with SessionLocal() as s:
            try:
                results["a"] = order_service.checkout(
                    s, _form(ids["method"]), user_id=None, session_token=token_a, locale="uk"
                )
                a_holds_lock.set() 
                time.sleep(HOLD_SECONDS)
                s.commit()
            except Exception as e:
                results["a"] = e
                a_holds_lock.set()  

    def buyer_b():
        assert a_holds_lock.wait(timeout=5)
        with SessionLocal() as s:
            s.execute(text("SET LOCAL lock_timeout = '5s'"))
            started = time.monotonic()
            try:
                results["b"] = order_service.checkout(
                    s, _form(ids["method"]), user_id=None, session_token=token_b, locale="uk"
                )
                s.commit()
            except Exception as e:
                s.rollback()
                results["b"] = e
            results["b_waited"] = time.monotonic() - started

    threads = [threading.Thread(target=buyer_a), threading.Thread(target=buyer_b)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=15)

    assert not isinstance(results.get("a"), Exception), results.get("a")
    assert isinstance(results.get("b"), order_service.OutOfStockError), results.get("b")
    assert results["b"].shortages[0]["available"] == 0
    assert results["b_waited"] >= HOLD_SECONDS * 0.8

    with SessionLocal() as s:
        variant = s.get(ProductVariant, ids["variant"])
        assert (variant.stock_quantity, variant.reserved_quantity) == (1, 1)
