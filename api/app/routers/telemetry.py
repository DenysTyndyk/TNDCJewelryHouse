from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.core.limiter import limiter
from app.dependencies import get_db
from app.routers.cart import CartOwner, get_cart_owner
from app.schemas.telemetry import EventBatchIn
from app.services import telemetry_service
from app.services.telemetry_service import TRACKING_CONSENT_HEADER

router = APIRouter(tags=["telemetry"])


@router.post("/events", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
@limiter.limit("30/minute")
def ingest_events(
    request: Request,
    batch: EventBatchIn,
    owner: CartOwner = Depends(get_cart_owner),
    x_tracking_consent: str | None = Header(default=None, alias=TRACKING_CONSENT_HEADER, max_length=16),
    db: Session = Depends(get_db),
):
    """Batch of UX events (max 50). Requires tracking consent: profile flag or X-Tracking-Consent for guests."""
    if not telemetry_service.tracking_allowed(db, owner.user_id, x_tracking_consent):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tracking consent required")
    telemetry_service.record_events(db, batch.events, user_id=owner.user_id, session_token=owner.session_token)
    db.commit()
