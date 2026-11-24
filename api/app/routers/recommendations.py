from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.dependencies import get_db
from app.routers.cart import CartOwner, get_cart_owner
from app.schemas.recommendation import RecommendationOut
from app.services import catalog_service, telemetry_service
from app.services.recommendation import engine

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

ConsentHeader = Annotated[
    str | None, Header(alias=telemetry_service.TRACKING_CONSENT_HEADER, max_length=16)
]

@router.get("/similar/{product_id}", response_model=RecommendationOut)
def similar(
    product_id: int,
    algorithm: Literal["cbf", "vector", "hybrid"] | None = Query(
        default=None, description="Override SIMILAR_SOURCE; vector/hybrid fall back to cbf without embeddings"
    ),
    owner: CartOwner = Depends(get_cart_owner),
    db: Session = Depends(get_db),
):
    source = algorithm or settings.similar_source
    try:
        algo, ids = engine.cached(
            db, f"similar:{source}:{product_id}", owner.user_id, owner.session_token,
            lambda: engine.similar(
                db, product_id, user_id=owner.user_id, session_token=owner.session_token, source=source
            ),
        )
    except engine.ProductNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found") from None
    db.commit()
    return RecommendationOut(algorithm=algo, items=catalog_service.product_cards(db, ids, owner.locale))

@router.get("/for-you", response_model=RecommendationOut)
def for_you(
    owner: CartOwner = Depends(get_cart_owner),
    x_tracking_consent: ConsentHeader = None,
    db: Session = Depends(get_db),
):
    tracking = telemetry_service.tracking_allowed(db, owner.user_id, x_tracking_consent)
    # tracking is part of the key: a withdrawn consent must not keep serving the history-based list.
    algo, ids = engine.cached(
        db, f"for_you:{int(tracking)}", owner.user_id, owner.session_token,
        lambda: engine.for_you(db, user_id=owner.user_id, session_token=owner.session_token, tracking=tracking),
    )
    db.commit()
    return RecommendationOut(algorithm=algo, items=catalog_service.product_cards(db, ids, owner.locale))

@router.get("/recently-viewed", response_model=RecommendationOut, summary="Products the owner viewed (needs consent)")
def recently_viewed(
    owner: CartOwner = Depends(get_cart_owner),
    x_tracking_consent: ConsentHeader = None,
    db: Session = Depends(get_db),
):
    tracking = telemetry_service.tracking_allowed(db, owner.user_id, x_tracking_consent)
    algo, ids = engine.recently_viewed(
        db, user_id=owner.user_id, session_token=owner.session_token, tracking=tracking
    )
    return RecommendationOut(algorithm=algo, items=catalog_service.product_cards(db, ids, owner.locale))

@router.get("/also-viewed/{product_id}", response_model=RecommendationOut, summary="Others also viewed (co-views)")
def also_viewed(product_id: int, owner: CartOwner = Depends(get_cart_owner), db: Session = Depends(get_db)):
    algo, ids = engine.also_viewed(db, product_id)
    return RecommendationOut(algorithm=algo, items=catalog_service.product_cards(db, ids, owner.locale))