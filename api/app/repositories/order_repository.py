from datetime import datetime, timezone

from sqlalchemy.orm import Session
from sqlalchemy import and_, func, select

from app.models.catalog import Product, ProductVariant
from app.models.commerce import Order, OrderItem
from app.models.logistics import ShippingMethod
from app.repositories.catalog_repository import IS_PUBLISHED


def list_active_shipping_methods(db: Session) -> list[ShippingMethod]:
    stmt = (
        select(ShippingMethod)
        .where(ShippingMethod.is_active.is_(True))
        .order_by(ShippingMethod.cost, ShippingMethod.id)
    )
    return list(db.scalars(stmt))

def get_active_shipping_method(db: Session, method_id: int) -> ShippingMethod | None:
    return db.scalar(
        select(ShippingMethod).where(ShippingMethod.id == method_id, ShippingMethod.is_active.is_(True))
    )


def lock_purchasable_variants(db: Session, variant_ids: list[int]) -> dict[int, ProductVariant]:
    stmt = (
        select(ProductVariant)
        .join(Product, Product.id == ProductVariant.product_id)
        .where(ProductVariant.id.in_(variant_ids), IS_PUBLISHED)
        .order_by(ProductVariant.id)
        .with_for_update(of=ProductVariant)
        .execution_options(populate_existing=True)
    )
    return {v.id: v for v in db.scalars(stmt)}


def next_order_number(db: Session) -> str:
    seq = db.scalar(select(func.nextval("order_number_seq")))
    return f"TNDC-{datetime.now(timezone.utc).year}-{seq:05d}"

def _owned_by(user_id: int | None, session_token: str | None):
    if user_id is not None:
        return Order.user_id == user_id
    return and_(Order.user_id.is_(None), Order.session_token == session_token)


def list_orders(db: Session, *, user_id: int | None, session_token: str | None, limit: int) -> list[Order]:
    stmt = (
        select(Order)
        .where(_owned_by(user_id, session_token))
        .order_by(Order.created_at.desc(), Order.id.desc())
        .limit(limit)
    )
    return list(db.scalars(stmt))


def get_order(
    db: Session,
    order_number: str,
    *,
    user_id: int | None,
    session_token: str | None,
    for_update: bool = False,
) -> Order | None:
    stmt = select(Order).where(Order.order_number == order_number, _owned_by(user_id, session_token))
    if for_update:
        stmt = stmt.with_for_update().execution_options(populate_existing=True)
    return db.scalar(stmt)

def list_order_items(db: Session, order_id: int) -> list[OrderItem]:
    return list(db.scalars(select(OrderItem).where(OrderItem.order_id == order_id).order_by(OrderItem.id)))

def lock_variants(db: Session, variant_ids: list[int]) -> dict[int, ProductVariant]:
    """FOR UPDATE in id order, without the published filter: a reserve must be released
    even if the product was unpublished after the order was placed."""
    stmt = (
        select(ProductVariant)
        .where(ProductVariant.id.in_(variant_ids))
        .order_by(ProductVariant.id)
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    return {v.id: v for v in db.scalars(stmt)}
