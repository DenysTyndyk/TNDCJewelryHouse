from datetime import datetime

from sqlalchemy import Date, cast, func, insert, select, update
from sqlalchemy.orm import Session

from app.models.catalog import Product
from app.models.enums import EventType
from app.models.telemetry import SearchQuery, UserEvent

# Single market (D3): a "day" in reports is a Kyiv calendar day, not a UTC one.
REPORT_TZ = "Europe/Kyiv"


def existing_ids(db: Session, model, ids: set[int]) -> set[int]:
    """Return the subset of ids that exist in model's table, in one query."""
    if not ids:
        return set()
    return set(db.scalars(select(model.id).where(model.id.in_(ids))))


def bulk_insert_events(db: Session, rows: list[dict]) -> None:
    if rows:
        db.execute(insert(UserEvent), rows)


def link_guest_events(db: Session, session_token: str, user_id: int) -> None:
    """Attach events collected as a guest to the account that just logged in (T3.5)."""
    for model in (UserEvent, SearchQuery):
        db.execute(
            update(model)
            .where(model.session_token == session_token, model.user_id.is_(None))
            .values(user_id=user_id)
        )


def anonymize_user_events(db: Session, user_id: int) -> None:
    """Detach all behaviour data from a user (RODO). Rows stay for aggregate stats (popularity)."""
    for model in (UserEvent, SearchQuery):
        db.execute(
            update(model)
            .where(model.user_id == user_id)
            .values(user_id=None, session_token=None)
        )

def anonymize_older_than(db: Session, cutoff: datetime) -> dict[str, int]:
    """Detach events/searches created before cutoff from people. Returns affected rows per table."""
    counts = {}
    for model in (UserEvent, SearchQuery):
        result = db.execute(
            update(model)
            .where(
                model.created_at < cutoff,
                (model.user_id.is_not(None)) | (model.session_token.is_not(None)),
            )
            .values(user_id=None, session_token=None)
        )
        counts[model.__tablename__] = result.rowcount
    return counts


def count_events_by_day(db: Session, since: datetime) -> list:
    day = cast(func.timezone(REPORT_TZ, UserEvent.created_at), Date).label("day")
    stmt = (
        select(day, UserEvent.event_type, func.count().label("count"))
        .where(UserEvent.created_at >= since)
        .group_by(day, UserEvent.event_type)
        .order_by(day, UserEvent.event_type)
    )
    return db.execute(stmt).all()


def top_products(db: Session, event_type: EventType, since: datetime, limit: int) -> list:
    count = func.count().label("count")
    stmt = (
        select(UserEvent.product_id, Product.slug, count)
        .join(Product, Product.id == UserEvent.product_id)
        .where(UserEvent.event_type == event_type, UserEvent.created_at >= since)
        .group_by(UserEvent.product_id, Product.slug)
        .order_by(count.desc(), UserEvent.product_id)
        .limit(limit)
    )
    return db.execute(stmt).all()