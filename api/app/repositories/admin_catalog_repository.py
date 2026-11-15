"""Write-side data access for the admin catalog. Commits are done by the service."""
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.catalog import CategoryTranslation, ProductImage, ProductTranslation, VariantPrice
from app.models.enums import Currency


def upsert_product_translation(db: Session, product_id: int, locale: str, data: dict) -> ProductTranslation:
    tr = db.scalar(
        select(ProductTranslation).where(
            ProductTranslation.product_id == product_id, ProductTranslation.locale == locale
        )
    )
    if tr is None:
        tr = ProductTranslation(product_id=product_id, locale=locale)
        db.add(tr)
    for field, value in data.items():
        setattr(tr, field, value)
    return tr


def upsert_category_translation(db: Session, category_id: int, locale: str, data: dict) -> CategoryTranslation:
    tr = db.scalar(
        select(CategoryTranslation).where(
            CategoryTranslation.category_id == category_id, CategoryTranslation.locale == locale
        )
    )
    if tr is None:
        tr = CategoryTranslation(category_id=category_id, locale=locale)
        db.add(tr)
    for field, value in data.items():
        setattr(tr, field, value)
    return tr


def get_price(db: Session, variant_id: int, currency: Currency) -> VariantPrice | None:
    return db.scalar(
        select(VariantPrice).where(VariantPrice.variant_id == variant_id, VariantPrice.currency == currency)
    )


def list_image_keys(db: Session, product_id: int) -> list[str]:
    return list(db.scalars(select(ProductImage.storage_key).where(ProductImage.product_id == product_id)))


def clear_primary_image(db: Session, product_id: int) -> None:
    db.execute(
        update(ProductImage)
        .where(ProductImage.product_id == product_id, ProductImage.is_primary)
        .values(is_primary=False)
    )
