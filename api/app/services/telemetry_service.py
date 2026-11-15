"""Behaviour telemetry (M5): consent rule and event intake."""

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.catalog import Category, Product, ProductVariant
from app.models.enums import EventType
from app.repositories import telemetry_repository, user_repository
from app.schemas.telemetry import EventIn

TRACKING_CONSENT_HEADER = "X-Tracking-Consent"
CONSENT_GRANTED = "granted"

_REFERENCES = {"product_id": Product, "variant_id": ProductVariant, "category_id": Category}


def tracking_allowed(db: Session, user_id: int | None, consent_header: str | None) -> bool:
    """Logged-in user: the stored profile flag decides, the header is ignored. Guest: the header."""
    if user_id is not None:
        profile = user_repository.get_profile(db, user_id)
        return profile is not None and profile.consent_analytics
    return consent_header == CONSENT_GRANTED


def record_events(db: Session, events: list[EventIn], *, user_id: int | None, session_token: str | None) -> None:
    """Store a validated batch. Events pointing at unknown products/variants/categories are dropped."""
    known = {
        field: telemetry_repository.existing_ids(
            db, model, {getattr(e, field) for e in events if getattr(e, field) is not None}
        )
        for field, model in _REFERENCES.items()
    }
    rows = [
        {
            "user_id": user_id,
            "session_token": session_token,
            "event_type": e.event_type,
            "product_id": e.product_id,
            "variant_id": e.variant_id,
            "category_id": e.category_id,
            "event_metadata": e.metadata,
            "source": e.source,
        }
        for e in events
        if all(getattr(e, field) is None or getattr(e, field) in known[field] for field in _REFERENCES)
    ]
    telemetry_repository.bulk_insert_events(db, rows)


def _since(days: int) -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=days)


def events_by_day(db: Session, days: int) -> list:
    return telemetry_repository.count_events_by_day(db, _since(days))


def top_products(db: Session, event_type: EventType, days: int, limit: int) -> list:
    return telemetry_repository.top_products(db, event_type, _since(days), limit)
