"""Import products from folders: one folder per product with product.json and photos.

    catalog_import/
    └── <product-slug>/          folder name = product slug
        ├── product.json
        ├── 1.jpg                photos in name order; the first one is the primary photo
        └── 2.jpg

Run from api/:

    python -m scripts.import_products ../catalog_import

Re-running is safe: the product is matched by slug and updated, variants by SKU,
gemstones and photos are replaced. Uses the same services as the admin API.
"""
import sys
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.models.catalog import Category, Gemstone, Product, ProductGemstone, ProductImage, ProductVariant
from app.schemas.admin_catalog import (
    PriceIn,
    ProductCreate,
    ProductGemstoneIn,
    ProductTranslationIn,
    ProductUpdate,
    VariantCreate,
    VariantUpdate,
)
from app.schemas.catalog import Locale
from app.services import admin_catalog_service as svc

PHOTO_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


class VariantFile(VariantCreate):
    model_config = ConfigDict(extra="forbid")
    sale_price: Decimal | None = Field(default=None, gt=0)


class GemstoneFile(ProductGemstoneIn):
    model_config = ConfigDict(extra="forbid")
    gemstone_id: int = 0  # filled from `gemstone` (slug)
    gemstone: str


class ProductFile(BaseModel):
    model_config = ConfigDict(extra="forbid")  # a typo in a key is an error, not a silently ignored field
    category: str
    published: bool = True
    is_featured: bool = False
    translations: dict[Locale, ProductTranslationIn]
    variants: list[VariantFile] = Field(min_length=1)
    gemstones: list[GemstoneFile] = []


def _by_slug(db: Session, model, slug: str) -> int:
    obj_id = db.scalar(select(model.id).where(model.slug == slug))
    if obj_id is None:
        raise ValueError(f"{model.__name__} '{slug}' does not exist")
    return obj_id


def import_product(db: Session, folder: Path) -> int:
    """Create or update one product from its folder; returns the product id."""
    slug = folder.name
    data = ProductFile.model_validate_json((folder / "product.json").read_text(encoding="utf-8"))
    if "uk" not in data.translations:
        raise ValueError("translations.uk is required")
    photos = sorted(p for p in folder.iterdir() if p.suffix.lower() in PHOTO_SUFFIXES)
    if not photos:
        raise ValueError("no photos (.jpg, .png, .webp) in the folder")
    for photo in photos:
        if photo.stat().st_size > svc.MAX_UPLOAD_BYTES:
            raise ValueError(f"{photo.name} is larger than 10 MB")

    category_id = _by_slug(db, Category, data.category)
    gemstone_ids = [_by_slug(db, Gemstone, g.gemstone) for g in data.gemstones]

    product = db.scalar(select(Product).where(Product.slug == slug))
    if product is None:
        product = svc.create_product(db, ProductCreate(category_id=category_id, slug=slug, is_featured=data.is_featured))
    else:
        svc.update_product(db, product.id, ProductUpdate(category_id=category_id, is_featured=data.is_featured))

    for locale, tr in data.translations.items():
        svc.set_product_translation(db, product.id, locale, tr)

    for v in data.variants:
        fields = v.model_dump(exclude={"sale_price"})
        variant = db.scalar(select(ProductVariant).where(ProductVariant.sku == v.sku))
        if variant is None:
            variant = svc.create_variant(db, product.id, VariantCreate(**fields))
        elif variant.product_id != product.id:
            raise ValueError(f"SKU {v.sku} already belongs to another product")
        else:
            svc.update_variant(db, variant.id, VariantUpdate(**fields))
        svc.set_price(db, variant.id, PriceIn(price=v.base_price, sale_price=v.sale_price))

    for link_id in db.scalars(select(ProductGemstone.id).where(ProductGemstone.product_id == product.id)).all():
        svc.remove_gemstone(db, product.id, link_id)
    for g, gemstone_id in zip(data.gemstones, gemstone_ids):
        svc.add_gemstone(db, product.id, ProductGemstoneIn(**g.model_dump(exclude={"gemstone", "gemstone_id"}), gemstone_id=gemstone_id))

    for photo in photos:
        svc.process_image(photo.read_bytes())
    for image_id in db.scalars(select(ProductImage.id).where(ProductImage.product_id == product.id)).all():
        svc.delete_image(db, image_id)
    name = data.translations["uk"].name
    for i, photo in enumerate(photos):
        svc.upload_image(db, product.id, photo.read_bytes(), f"{name}, фото {i + 1}", is_primary=i == 0)

    if not data.published:
        svc.update_product(db, product.id, ProductUpdate(published_at=None))
    elif product.published_at is None:
        svc.update_product(db, product.id, ProductUpdate(published_at=datetime.now(timezone.utc)))
    return product.id


def import_all(db: Session, root: Path) -> tuple[int, list[str]]:
    """Import every product folder; returns (imported count, error messages)."""
    folders = sorted(p for p in root.iterdir() if (p / "product.json").is_file())
    imported, errors = 0, []
    for folder in folders:
        try:
            import_product(db, folder)
            imported += 1
            print(f"OK    {folder.name}")
        except (ValueError, svc.NotFoundError, svc.ConflictError, svc.InvalidImageError) as exc:
            errors.append(f"{folder.name}: {exc}")
            print(f"ERROR {folder.name}: {exc}")
    return imported, errors


def main() -> None:
    if len(sys.argv) != 2 or not Path(sys.argv[1]).is_dir():
        sys.exit("Usage: python -m scripts.import_products <folder>")
    session = get_session()
    try:
        imported, errors = import_all(session, Path(sys.argv[1]))
    finally:
        session.close()
    print(f"\nImported: {imported}, errors: {len(errors)}")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
