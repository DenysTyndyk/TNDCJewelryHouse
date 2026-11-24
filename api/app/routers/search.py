from typing import Annotated

from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.routers.cart import CartOwner, get_cart_owner
from app.schemas.search import SearchOut, SearchParams
from app.services import catalog_service, telemetry_service
from app.services.search import service as search_service

router = APIRouter(tags=["search"])


@router.get("/search", response_model=SearchOut, summary="Product search: lexical, semantic or hybrid (RRF)")
def search(
    params: Annotated[SearchParams, Query()],
    owner: CartOwner = Depends(get_cart_owner),
    x_tracking_consent: str | None = Header(
        default=None, alias=telemetry_service.TRACKING_CONSENT_HEADER, max_length=16
    ),
    db: Session = Depends(get_db),
):
    tracking = telemetry_service.tracking_allowed(db, owner.user_id, x_tracking_consent)
    result = search_service.search(
        db, params.q, params.mode, params, owner.locale,
        offset=params.offset,
        user_id=owner.user_id,
        session_token=owner.session_token,
        tracking=tracking,
    )
    db.commit()  
    return SearchOut(
        mode_used=result.mode_used,
        total=result.total,
        items=catalog_service.product_cards(db, result.ids, owner.locale),
    )