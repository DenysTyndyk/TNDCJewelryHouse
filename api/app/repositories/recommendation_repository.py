from datetime import UTC, datetime, timedelta
from sqlalchemy import String, and_, cast, func, null, or_, select,delete
from sqlalchemy.orm import Session, aliased

from app.models.catalog import Product, ProductGemstone, ProductVariant, VariantPrice
from app.models.commerce import Cart, CartItem, Order, OrderItem , CartStatus
from app.models.enums import Currency, EventType, OrderStatus
from app.models.telemetry import UserEvent,RecommendationCache
from app.repositories.catalog_repository import AVAILABLE, EFFECTIVE_PRICE, IS_PUBLISHED
from sqlalchemy.dialects.postgresql import insert
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

def recently_viewed(db: Session, *, user_id: int | None, session_token: str | None, limit: int) -> list[int]:
    """Products the owner viewed, each once, most recent first."""
    if user_id is None and not session_token:
        return []
    stmt = (
        select(UserEvent.product_id)
        .where(
            _owner(UserEvent, user_id, session_token),
            UserEvent.event_type == EventType.ProductView,
            UserEvent.product_id.is_not(None),
        )
        .group_by(UserEvent.product_id)
        .order_by(func.max(UserEvent.created_at).desc())
        .limit(limit)
    )
    return list(db.scalars(stmt))

def also_viewed(db: Session, product_id: int, *, since: datetime, limit: int) -> list[int]:
    """Item-to-item co-views: products viewed by the same people who viewed product_id."""
    me, other = aliased(UserEvent), aliased(UserEvent)
    same_person = or_(
        and_(me.user_id.is_not(None), other.user_id == me.user_id),
        and_(me.user_id.is_(None), other.session_token == me.session_token),
    )
    # Ranked by distinct viewers, so one person reopening a product 30 times does not dominate.
    viewers = func.count(func.distinct(func.coalesce(cast(other.user_id, String), other.session_token)))
    stmt = (
        select(other.product_id)
        .select_from(me)
        .join(other, and_(
            same_person,
            other.event_type == EventType.ProductView,
            other.product_id.is_not(None),
            other.product_id != product_id,
            other.created_at >= since,
        ))
        .where(me.product_id == product_id, me.event_type == EventType.ProductView, me.created_at >= since)
        .group_by(other.product_id)
        .order_by(viewers.desc(), other.product_id)
        .limit(limit)
    )
    return list(db.scalars(stmt))

def cache_get(db: Session, key: str) -> RecommendationCache | None:
    row = db.get(RecommendationCache, key)
    return row if row and row.expires_at > datetime.now(UTC) else None

def cache_put(db: Session, key: str, owner_key: str, algorithm: str, ids: list[int], ttl_seconds: int) -> None:
    now = datetime.now(UTC)
    db.execute(delete(RecommendationCache).where(RecommendationCache.expires_at < now))
    stmt = insert(RecommendationCache).values(
        cache_key=key, owner_key=owner_key, algorithm=algorithm,
        product_ids=ids, expires_at=now + timedelta(seconds=ttl_seconds),
    )
    db.execute(stmt.on_conflict_do_update(
        index_elements=["cache_key"],
        set_={"algorithm": stmt.excluded.algorithm, "product_ids": stmt.excluded.product_ids,
              "expires_at": stmt.excluded.expires_at},
    ))

def cache_drop_owner(db: Session, owner_key: str) -> None:
    db.execute(delete(RecommendationCache).where(RecommendationCache.owner_key == owner_key))