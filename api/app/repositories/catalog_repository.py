import base64
import json
from datetime import datetime
from decimal import Decimal, InvalidOperation

from sqlalchemy import and_, case, func, or_, select, tuple_
from sqlalchemy.orm import Session, aliased

from app.models.catalog import (
    Category,
    CategoryTranslation,
    Gemstone,
    Product,
    ProductGemstone,
    ProductImage,
    ProductTranslation,
    ProductVariant,
    VariantPrice,
)
from app.models.enums import Currency
from app.schemas.catalog import ProductFilter

DEFAULT_LOCALE = "uk"  

_now = func.now()

SALE_ACTIVE = and_(
    VariantPrice.sale_price.is_not(None),
    or_(VariantPrice.sale_starts_at.is_(None), VariantPrice.sale_starts_at <= _now),
    or_(VariantPrice.sale_ends_at.is_(None), VariantPrice.sale_ends_at > _now),
)
EFFECTIVE_PRICE = case((SALE_ACTIVE, VariantPrice.sale_price), else_=VariantPrice.price)
AVAILABLE = ProductVariant.stock_quantity - ProductVariant.reserved_quantity
IS_PUBLISHED = and_(Product.published_at.is_not(None), Product.published_at <= _now)

def list_categories(db: Session, locale: str):
    tr = aliased(CategoryTranslation)
    tr_default = aliased(CategoryTranslation)
    stmt = (
        select(
            Category.id,
            Category.parent_id,
            Category.slug,
            func.coalesce(tr.name, tr_default.name, Category.slug).label("name"),
            case((tr.id.is_not(None), tr.description), else_= tr_default.description).label("description"),
        )
        .outerjoin(tr,and_(tr.category_id == Category.id, tr.locale == locale))
        .outerjoin(tr_default, and_(tr_default.category_id == Category.id, tr_default.locale == DEFAULT_LOCALE))
        .where(Category.is_active)
        .order_by(Category.sort_order, Category.id)
    )
    return db.execute(stmt).all()

_SORT_PARSERS = {
    "newest": datetime.fromisoformat,
    "price_asc": Decimal,
    "price_desc": Decimal,
    "popular": int,
}

def _encode_cursor(sort_value, last_id: int) -> str:
    raw = json.dumps([str(sort_value), last_id])
    return base64.urlsafe_b64encode(raw.encode()).decode()


def _decode_cursor(cursor: str, sort: str):
    try:
        raw_value, last_id = json.loads(base64.urlsafe_b64decode(cursor))
        return _SORT_PARSERS[sort](raw_value), int(last_id)
    except (ValueError, TypeError, KeyError, InvalidOperation) as exc:
        raise ValueError("invalid cursor") from exc

def list_products(db: Session, filters: ProductFilter, currency: Currency):
    offers = (
        select(
            ProductVariant.product_id,
            func.min(EFFECTIVE_PRICE).label("price_from"),
            func.bool_or(SALE_ACTIVE).label("has_sale"),
            func.bool_or(AVAILABLE > 0).label("in_stock"),
        )
        .join(
            VariantPrice,
            and_(
                VariantPrice.variant_id == ProductVariant.id,
                VariantPrice.currency == currency,
                VariantPrice.is_active,
            ),
        )
        .group_by(ProductVariant.product_id)
    )
    if filters.metal:
        offers = offers.where(ProductVariant.metal_type == filters.metal)
    if filters.color:
        offers = offers.where(ProductVariant.metal_color == filters.color)
    if filters.fineness:
        offers = offers.where(ProductVariant.fineness == filters.fineness)
    if filters.in_stock: 
        offers = offers.where(AVAILABLE > 0)
    offers = offers.subquery()

    tr = aliased(ProductTranslation)
    tr_default = aliased(ProductTranslation)
    sort_col = {
        "newest": Product.published_at,
        "price_asc": offers.c.price_from,
        "price_desc": offers.c.price_from,
        "popular": Product.view_count,
    }[filters.sort]
    ascending = filters.sort == "price_asc"

    stmt = (
        select(
            Product.id,
            Product.slug,
            Product.is_featured,
            Category.slug.label("category_slug"),
            func.coalesce(tr.name, tr_default.name, Product.slug).label("name"),
            offers.c.price_from,
            offers.c.has_sale,
            offers.c.in_stock,
            sort_col.label("sort_value"),
        )
        .join(offers, offers.c.product_id == Product.id)
        .join(Category, Category.id == Product.category_id)
        .outerjoin(tr, and_(tr.product_id == Product.id, tr.locale == filters.locale))
        .outerjoin(tr_default, and_(tr_default.product_id == Product.id, tr_default.locale == DEFAULT_LOCALE))
        .where(IS_PUBLISHED)
    )

    if filters.price_min is not None:
        stmt = stmt.where(offers.c.price_from >= filters.price_min)
    if filters.price_max is not None:
        stmt = stmt.where(offers.c.price_from <= filters.price_max)

    if filters.category:
        tree = (
            select(Category.id)
            .where(Category.slug == filters.category)
            .cte("category_tree", recursive=True)
        )
        child = aliased(Category)
        tree = tree.union_all(select(child.id).where(child.parent_id == tree.c.id))
        stmt = stmt.where(Product.category_id.in_(select(tree.c.id)))

    if filters.gemstone:
        stmt = stmt.where(
            select(ProductGemstone.id)
            .join(Gemstone, Gemstone.id == ProductGemstone.gemstone_id)
            .where(ProductGemstone.product_id == Product.id, Gemstone.slug == filters.gemstone)
            .exists()
        )

    if filters.cursor:
        value, last_id = _decode_cursor(filters.cursor, filters.sort)
        key, after = tuple_(sort_col, Product.id), tuple_(value, last_id)
        stmt = stmt.where(key > after if ascending else key < after)

    order = (sort_col.asc(), Product.id.asc()) if ascending else (sort_col.desc(), Product.id.desc())
    rows = db.execute(stmt.order_by(*order).limit(filters.limit + 1)).all()

    next_cursor = None
    if len(rows) > filters.limit:
        rows = rows[: filters.limit]
        next_cursor = _encode_cursor(rows[-1].sort_value, rows[-1].id)
    return rows, next_cursor

def list_primary_images(db: Session, product_ids: list[int]):
    if not product_ids:
        return []
    stmt = (
        select(ProductImage)
        .where(ProductImage.product_id.in_(product_ids))
        .order_by(ProductImage.product_id, ProductImage.is_primary.desc(), ProductImage.sort_order, ProductImage.id)
        .distinct(ProductImage.product_id)
    )
    return list(db.scalars(stmt))

def get_product_by_slug(db: Session, slug: str, locale: str):
    tr = aliased(ProductTranslation)
    tr_default = aliased(ProductTranslation)
    ctr = aliased(CategoryTranslation)
    ctr_default = aliased(CategoryTranslation)
    has_tr = tr.id.is_not(None)
    stmt = (
        select(
            Product.id,
            Product.slug,
            func.coalesce(tr.name, tr_default.name, Product.slug).label("name"),
            case((has_tr, tr.description), else_=tr_default.description).label("description"),
            case((has_tr, tr.meta_title), else_=tr_default.meta_title).label("meta_title"),
            case((has_tr, tr.meta_description), else_=tr_default.meta_description).label("meta_description"),
            Category.id.label("category_id"),
            Category.slug.label("category_slug"),
            func.coalesce(ctr.name, ctr_default.name, Category.slug).label("category_name"),
        )
        .join(Category, Category.id == Product.category_id)
        .outerjoin(tr, and_(tr.product_id == Product.id, tr.locale == locale))
        .outerjoin(tr_default, and_(tr_default.product_id == Product.id, tr_default.locale == DEFAULT_LOCALE))
        .outerjoin(ctr, and_(ctr.category_id == Category.id, ctr.locale == locale))
        .outerjoin(ctr_default, and_(ctr_default.category_id == Category.id, ctr_default.locale == DEFAULT_LOCALE))
        .where(Product.slug == slug, IS_PUBLISHED)
    )
    return db.execute(stmt).one_or_none()


def list_variants(db: Session, product_id: int, currency: Currency):
    stmt = (
        select(
            ProductVariant,
            VariantPrice.price,
            case((SALE_ACTIVE, VariantPrice.sale_price)).label("sale_price"),  # NULL when no active sale
            (AVAILABLE > 0).label("in_stock"),
        )
        .join(
            VariantPrice,
            and_(
                VariantPrice.variant_id == ProductVariant.id,
                VariantPrice.currency == currency,
                VariantPrice.is_active,
            ),
        )
        .where(ProductVariant.product_id == product_id)
        .order_by(ProductVariant.id)
    )
    return db.execute(stmt).all()


def list_images(db: Session, product_id: int):
    stmt = (
        select(ProductImage)
        .where(ProductImage.product_id == product_id)
        .order_by(ProductImage.is_primary.desc(), ProductImage.sort_order, ProductImage.id)
    )
    return list(db.scalars(stmt))

def list_gemstones(db: Session, product_id: int):
    stmt = (
        select(ProductGemstone, Gemstone.slug, Gemstone.name)
        .join(Gemstone, Gemstone.id == ProductGemstone.gemstone_id)
        .where(ProductGemstone.product_id == product_id)
        .order_by(ProductGemstone.is_center_stone.desc(), ProductGemstone.id)
    )
    return db.execute(stmt).all()
