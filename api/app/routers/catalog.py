from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.catalog import CategoryNode, Locale, ProductDetail, ProductFilter, ProductPage
from app.services import catalog_service
from app.services.catalog_service import InvalidCursorError, ProductNotFoundError

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
    db: Session = Depends(get_db),
):
    try:
        return catalog_service.list_products(db, filters, accept_language)
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
