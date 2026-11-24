from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.routers.cart import CartOwner, get_cart_owner
from app.routers.recommendations import ConsentHeader
from app.schemas.catalog import CategoryNode, Locale, ProductDetail, ProductFilter, ProductPage
from app.services import catalog_service, telemetry_service
from app.services.catalog_service import InvalidCursorError, ProductNotFoundError
from app.services.recommendation import engine

router = APIRouter(tags=["catalog"])

@router.get("/categories", response_model=list[CategoryNode])
def list_categories(
    locale: Locale | None = None,
    accept_language: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    return catalog_service.get_category_tree(db, catalog_service.resolve_locale(locale, accept_language))

@router.get("/products", response_model=ProductPage)
def list_products(
    filters: Annotated[ProductFilter, Query()],
    accept_language: str | None = Header(default=None),
    owner: CartOwner = Depends(get_cart_owner),
    x_tracking_consent: ConsentHeader = None,
    db: Session = Depends(get_db),
):
    ranked = None
    if filters.sort == "recommended":
        tracking = telemetry_service.tracking_allowed(db, owner.user_id, x_tracking_consent)
        # Cached: without it every catalog page would recompute the hybrid ranking.
        _, ranked = engine.cached(
            db, f"rank:{int(tracking)}", owner.user_id, owner.session_token,
            lambda: engine.ranking(db, user_id=owner.user_id, session_token=owner.session_token, tracking=tracking),
        )
        db.commit()
    try:
        return catalog_service.list_products(db, filters, accept_language, ranked=ranked)
    except InvalidCursorError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/products/{slug}", response_model=ProductDetail)
def get_product(
    slug: str,
    locale: Locale | None = None,
    accept_language: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    try:
        return catalog_service.get_product(db, slug, catalog_service.resolve_locale(locale, accept_language))
    except ProductNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
