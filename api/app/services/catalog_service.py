from typing import get_args

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.catalog import ProductImage
from app.models.enums import Currency
from app.repositories import catalog_repository as repo
from app.services.admin_catalog_service import IMAGE_WIDTHS
from app.schemas.catalog import (
    CategoryNode,
    ImageOut,
    Locale,
    ProductDetail,
    ProductFilter,
    ProductListItem,
    ProductPage,
    VariantOut,
    GemstoneOut,
)

SUPPORTED_LOCALES = get_args(Locale)  
DEFAULT_LOCALE = "uk"
CURRENCY = Currency.UAH


class ProductNotFoundError(Exception):
    pass


class InvalidCursorError(Exception):
    pass

def resolve_locale(query_locale: str | None, accept_language: str | None) -> str:
    """Pick the locale: ?locale= → Accept-Language → uk."""
    if query_locale:
        return query_locale
    for part in (accept_language or "").split(","):
        lang = part.split(";")[0].strip()[:2].lower()  # "pl-PL;q=0.9" → "pl"
        if lang in SUPPORTED_LOCALES:
            return lang
    return DEFAULT_LOCALE

def get_category_tree(db: Session, locale: str) -> list[CategoryNode]:
    rows = repo.list_categories(db, locale)
    nodes = {
        r.id: CategoryNode(id=r.id, slug=r.slug, name=r.name, description=r.description)
        for r in rows
    }
    roots: list[CategoryNode] = []
    for r in rows:
        if r.parent_id is None:
            roots.append(nodes[r.id])
        elif r.parent_id in nodes:
            nodes[r.parent_id].children.append(nodes[r.id])
    return roots

def _image_out(img: ProductImage) -> ImageOut:
    base = f"{settings.media_base_url}/{img.storage_key}"
    if "." in img.storage_key.rsplit("/", 1)[-1]:
        url, srcset = base, None  
    else:  
        url = f"{base}-800.webp"
        srcset = ", ".join(f"{base}-{w}.webp {w}w" for w in IMAGE_WIDTHS)
    return ImageOut(
        id=img.id,
        url=url,
        srcset=srcset,
        alt_text=img.alt_text,
        width=img.width,
        height=img.height,
        is_primary=img.is_primary,
        variant_id=img.variant_id,
    )

def list_products(db: Session, filters: ProductFilter, accept_language: str | None) -> ProductPage:
    locale = resolve_locale(filters.locale, accept_language)
    filters = filters.model_copy(update={"locale": locale})

    try:
        rows, next_cursor = repo.list_products(db, filters, CURRENCY)
    except ValueError as exc:  
        raise InvalidCursorError("Invalid cursor") from exc

    images = {
        img.product_id: _image_out(img)
        for img in repo.list_primary_images(db, [r.id for r in rows])
    }

    items = [
        ProductListItem(
            id=r.id,
            slug=r.slug,
            name=r.name,
            category_slug=r.category_slug,
            price_from=r.price_from,
            currency=CURRENCY,
            has_sale=r.has_sale,
            in_stock=r.in_stock,
            is_featured=r.is_featured,
            image=images.get(r.id),
        )
        for r in rows
    ]
    return ProductPage(items=items, next_cursor=next_cursor)

def get_product(db: Session, slug: str, locale: str) -> ProductDetail:
    row = repo.get_product_by_slug(db, slug, locale)
    if row is None:
        raise ProductNotFoundError(slug)

    variants = [
        VariantOut(
            id=v.ProductVariant.id,
            sku=v.ProductVariant.sku,
            size=v.ProductVariant.size,
            length_mm=v.ProductVariant.length_mm,
            weight=v.ProductVariant.weight,
            metal_type=v.ProductVariant.metal_type,
            metal_color=v.ProductVariant.metal_color,
            fineness=v.ProductVariant.fineness,
            price=v.price,
            sale_price=v.sale_price,
            currency=CURRENCY,
            in_stock=v.in_stock,
        )
        for v in repo.list_variants(db, row.id, CURRENCY)
    ]

    return ProductDetail(
        id=row.id,
        slug=row.slug,
        name=row.name,
        description=row.description,
        meta_title=row.meta_title,
        meta_description=row.meta_description,
        category=CategoryNode(id=row.category_id, slug=row.category_slug, name=row.category_name),
        variants=variants,
        images=[_image_out(img) for img in repo.list_images(db, row.id)],
        gemstones=[
            GemstoneOut(
                slug=g.slug,
                name=g.name,
                gemstone_type=g.ProductGemstone.gemstone_type,
                quantity=g.ProductGemstone.quantity,
                carat=g.ProductGemstone.carat,
                cut_type=g.ProductGemstone.cut_type,
                color_grade=g.ProductGemstone.color_grade,
                clarity_grade=g.ProductGemstone.clarity_grade,
                is_center_stone=g.ProductGemstone.is_center_stone,
                variant_id=g.ProductGemstone.variant_id,
            )
            for g in repo.list_gemstones(db, row.id)
        ],

    )
