from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.routers.cart import CartOwner, get_cart_owner
from app.schemas.recommendation import RecommendationOut
from app.services import catalog_service, telemetry_service
from app.services.recommendation import engine

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

@router.get("/similar/{product_id}", response_model=RecommendationOut)
def similar(product_id: int, owner: CartOwner = Depends(get_cart_owner), db: Session = Depends(get_db)):
    try:
        algorithm, ids = engine.similar(db, product_id, user_id=owner.user_id, session_token=owner.session_token)
    except engine.ProductNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found") from None
    return RecommendationOut(algorithm=algorithm, items=catalog_service.product_cards(db, ids, owner.locale))

@router.get("/for-you", response_model=RecommendationOut)
def for_you(
    owner: CartOwner = Depends(get_cart_owner),
    x_tracking_consent: str | None = Header(
        default=None, alias=telemetry_service.TRACKING_CONSENT_HEADER, max_length=16
    ),
    db: Session = Depends(get_db),
):
    tracking = telemetry_service.tracking_allowed(db, owner.user_id, x_tracking_consent)
    algorithm, ids = engine.for_you(
        db, user_id=owner.user_id, session_token=owner.session_token, tracking=tracking
    )
    return RecommendationOut(algorithm=algorithm, items=catalog_service.product_cards(db, ids, owner.locale))