from datetime import datetime

from sqlalchemy import String, and_, cast, func, null, select
from sqlalchemy.orm import Session

from app.models.catalog import Product, ProductGemstone, ProductVariant, VariantPrice
from app.models.commerce import Cart, CartItem, Order, OrderItem , CartStatus
from app.models.enums import Currency, EventType, OrderStatus
from app.models.telemetry import UserEvent
from app.repositories.catalog_repository import AVAILABLE, EFFECTIVE_PRICE, IS_PUBLISHED

def _distinct_array(column): 
    return func.array_remove(func.array_agg(column.distinct()), null())

def _owner(model,user_id: int | None, session_token: str| None):
    if user_id is not None:
        return model.user_id == user_id
    return model.session_token == session_token

def load_product_features(db: Session) -> list:
    variants = (
        select(
            ProductVariant.product_id,
            _distinct_array(cast(ProductVariant.metal_type, String)).label("metals"),
            _distinct_array(cast(ProductVariant.metal_color, String)).label("colors"),
            _distinct_array(ProductVariant.fineness).label("finenesses"),
            func.min(EFFECTIVE_PRICE).label("price"),
            func.bool_or(AVAILABLE > 0).label("available"),
        )
        .join(
             VariantPrice,
            and_(
                VariantPrice.variant_id == ProductVariant.id,
                VariantPrice.currency == Currency.UAH,
                VariantPrice.is_active,
            ),
        )
        .group_by(ProductVariant.product_id)
        .subquery()
    )
    gems = (
        select(
            ProductGemstone.product_id,
            _distinct_array(ProductGemstone.gemstone_id).label("gemstones"),
        )
        .group_by(ProductGemstone.product_id)
        .subquery()
    )
    stmt = (
        select(
            Product.id,
            Product.category_id,
            Product.published_at,
            variants.c.metals,
            variants.c.colors,
            variants.c.finenesses,
            variants.c.price,
            variants.c.available,
            gems.c.gemstones,
        )
        .join(variants, variants.c.product_id == Product.id)
        .outerjoin(gems, gems.c.product_id == Product.id)
        .where(IS_PUBLISHED)
    )
    return db.execute(stmt).all()

def user_events_for(
    db: Session,
    *,
    user_id: int | None,
    session_token: str | None,
    since: datetime,
    event_types: list[EventType],
) -> list:
    if user_id is None and not session_token:
        return []
    stmt = select(UserEvent.product_id, UserEvent.event_type, UserEvent.created_at).where(
        _owner(UserEvent, user_id, session_token),
        UserEvent.created_at >= since,
        UserEvent.product_id.is_not(None),
        UserEvent.event_type.in_(event_types),
    )
    return db.execute(stmt).all()

def event_counts(
    db: Session,
    *,
    short_since: datetime,
    long_since: datetime,
    event_types: list[EventType],
) -> list:
    stmt = (
        select(
            UserEvent.product_id,
            func.count().filter(UserEvent.created_at >= short_since).label("short_count"),
            func.count().label("long_count"),
        )
        .where(
            UserEvent.created_at >= long_since,
            UserEvent.product_id.is_not(None),
            UserEvent.event_type.in_(event_types),
        )
        .group_by(UserEvent.product_id)
    )
    return db.execute(stmt).all()

def purchased_product_ids(
    db: Session, *, user_id: int | None, session_token: str | None
) -> set[int]:
    if user_id is None and not session_token:
        return set()
    stmt = (
        select(OrderItem.product_id)
        .distinct()
        .join(Order, Order.id == OrderItem.order_id)
        .where(_owner(Order, user_id, session_token), Order.status != OrderStatus.Cancelled)
    )
    return set(db.scalars(stmt))

def cart_product_ids(db: Session, *, user_id: int | None, session_token: str | None) -> set[int]:
    if user_id is None and not session_token:
        return set()
    stmt = (
        select(ProductVariant.product_id)
        .distinct()
        .join(CartItem, CartItem.variant_id == ProductVariant.id)
        .join(Cart, Cart.id == CartItem.cart_id)
        .where(_owner(Cart, user_id, session_token), Cart.status == CartStatus.Active)
    )
    return set(db.scalars(stmt))