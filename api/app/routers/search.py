from typing import Annotated

from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.routers.cart import CartOwner, get_cart_owner
from app.repositories import search_repository
from app.schemas.catalog import Locale
from app.schemas.search import SearchOut, SearchParams, SuggestOut
from app.services import catalog_service, telemetry_service
from app.services.search import service as search_service

router = APIRouter(tags=["search"])

SUGGEST_LIMIT = 6


@router.get("/search/suggest", response_model=list[SuggestOut], summary="Header autocomplete by product name (not logged)")
def suggest(
    q: str = Query(min_length=2, max_length=100),
    locale: Locale | None = None,
    accept_language: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    # A separate endpoint: /search on every keystroke would flood search_queries analytics.
    rows = search_repository.suggest(
        db, q.strip(), catalog_service.resolve_locale(locale, accept_language), SUGGEST_LIMIT
    )
    return [SuggestOut(slug=r.slug, name=r.name) for r in rows]


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