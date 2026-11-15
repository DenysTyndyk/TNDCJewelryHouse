"""Admin analytics over behaviour telemetry (aggregates only, no personal data)."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_role
from app.models.enums import EventType, Role
from app.schemas.telemetry import EventCountOut, TopProductOut
from app.services import telemetry_service

# No token → 401 (get_current_user), role User → 403 (require_role)
router = APIRouter(
    prefix="/admin/analytics",
    tags=["admin"],
    dependencies=[Depends(require_role(Role.Manager, Role.Admin))],
)

Days = Query(default=30, ge=1, le=365)


@router.get("/events", response_model=list[EventCountOut])
def events_by_day(days: int = Days, db: Session = Depends(get_db)):
    """Event counts per Kyiv calendar day and type for the last `days` days."""
    return [EventCountOut.model_validate(r, from_attributes=True)
            for r in telemetry_service.events_by_day(db, days)]


@router.get("/top-products", response_model=list[TopProductOut])
def top_products(
    event_type: EventType = EventType.ProductView,
    days: int = Days,
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Most frequent products for one event type (views, add-to-cart, purchases...)."""
    return [TopProductOut.model_validate(r, from_attributes=True)
            for r in telemetry_service.top_products(db, event_type, days, limit)]
