"""Admin catalog API. Every endpoint requires a Manager or Admin access token."""
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_role
from app.models.enums import Role
from app.schemas.admin_catalog import (
    CategoryAdminOut,
    CategoryCreate,
    CategoryUpdate,
    ImageAdminOut,
    PriceIn,
    PriceOut,
    ProductAdminOut,
    ProductCreate,
    ProductGemstoneIn,
    ProductGemstoneOut,
    ProductTranslationIn,
    ProductTranslationOut,
    ProductUpdate,
    VariantAdminOut,
    VariantCreate,
    VariantUpdate,
)
from app.schemas.catalog import Locale
from app.services import admin_catalog_service as svc

# No token → 401 (get_current_user), role User → 403 (require_role)
router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_role(Role.Manager, Role.Admin))],
)

# --- categories ---

@router.post("/categories", response_model=CategoryAdminOut, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    return svc.create_category(db, payload)


@router.patch("/categories/{category_id}", response_model=CategoryAdminOut)
def update_category(category_id: int, payload: CategoryUpdate, db: Session = Depends(get_db)):
    return svc.update_category(db, category_id, payload)


# --- products ---

@router.post("/products", response_model=ProductAdminOut, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    return svc.create_product(db, payload)


@router.patch("/products/{product_id}", response_model=ProductAdminOut)
def update_product(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db)):
    return svc.update_product(db, product_id, payload)


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    svc.delete_product(db, product_id)


@router.put("/products/{product_id}/translations/{locale}", response_model=ProductTranslationOut)
def set_product_translation(
    product_id: int, locale: Locale, payload: ProductTranslationIn, db: Session = Depends(get_db)
):
    return svc.set_product_translation(db, product_id, locale, payload)


# --- variants and prices ---

@router.post("/products/{product_id}/variants", response_model=VariantAdminOut, status_code=status.HTTP_201_CREATED)
def create_variant(product_id: int, payload: VariantCreate, db: Session = Depends(get_db)):
    return svc.create_variant(db, product_id, payload)


@router.patch("/variants/{variant_id}", response_model=VariantAdminOut)
def update_variant(variant_id: int, payload: VariantUpdate, db: Session = Depends(get_db)):
    return svc.update_variant(db, variant_id, payload)


@router.delete("/variants/{variant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_variant(variant_id: int, db: Session = Depends(get_db)):
    svc.delete_variant(db, variant_id)


@router.put("/variants/{variant_id}/price", response_model=PriceOut)
def set_price(variant_id: int, payload: PriceIn, db: Session = Depends(get_db)):
    return svc.set_price(db, variant_id, payload)


# --- gemstones ---

@router.post("/products/{product_id}/gemstones", response_model=ProductGemstoneOut, status_code=status.HTTP_201_CREATED)
def add_gemstone(product_id: int, payload: ProductGemstoneIn, db: Session = Depends(get_db)):
    return svc.add_gemstone(db, product_id, payload)


@router.delete("/products/{product_id}/gemstones/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_gemstone(product_id: int, link_id: int, db: Session = Depends(get_db)):
    svc.remove_gemstone(db, product_id, link_id)


# --- images ---

@router.post("/products/{product_id}/images", response_model=ImageAdminOut, status_code=status.HTTP_201_CREATED)
def upload_image(
    product_id: int,
    file: UploadFile = File(...),
    alt_text: str | None = Form(default=None, max_length=255),
    is_primary: bool = Form(default=False),
    db: Session = Depends(get_db),
):
    data = file.file.read(svc.MAX_UPLOAD_BYTES + 1)
    if len(data) > svc.MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File is larger than 10 MB")
    return svc.upload_image(db, product_id, data, alt_text, is_primary)


@router.delete("/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_image(image_id: int, db: Session = Depends(get_db)):
    svc.delete_image(db, image_id)
