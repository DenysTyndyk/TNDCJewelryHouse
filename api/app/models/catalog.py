from datetime import datetime
from decimal import Decimal
from typing import Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, bigint_pk, created_at_col, int_pk, updated_at_col
from app.models.enums import (
    Currency,
    GemstoneType,
    MetalColor,
    MetalType,
    pg_enum,
)

EMBEDDING_DIM = 384  # intfloat/multilingual-e5-small (D5)


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int_pk]
    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL")
    )
    slug: Mapped[str] = mapped_column(String(120), unique=True)
    is_active: Mapped[bool] = mapped_column(server_default=text("true"))
    sort_order: Mapped[int] = mapped_column(server_default=text("0"))

    __table_args__ = (Index("ix_categories_parent_id", "parent_id"),)


class CategoryTranslation(Base):
    __tablename__ = "category_translations"

    id: Mapped[bigint_pk]
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"))
    locale: Mapped[str] = mapped_column(String(10))  # uk, pl, en
    name: Mapped[str] = mapped_column(String(150))
    description: Mapped[Optional[str]] = mapped_column(Text)

    __table_args__ = (
        Index("uq_category_translations_category_locale", "category_id", "locale", unique=True),
    )


class Product(Base):
    __tablename__ = "products"

    id: Mapped[bigint_pk]
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="RESTRICT"))
    slug: Mapped[str] = mapped_column(String(160), unique=True)
    is_featured: Mapped[bool] = mapped_column(server_default=text("false"))
    published_at: Mapped[Optional[datetime]]
    view_count: Mapped[int] = mapped_column(server_default=text("0"))
    # Lexical half of hybrid search (M7). Filled by the application from translations.
    search_vector: Mapped[Optional[str]] = mapped_column(TSVECTOR)
    created_at: Mapped[created_at_col]
    updated_at: Mapped[updated_at_col]

    __table_args__ = (
        Index("ix_products_category_id", "category_id"),
        Index("ix_products_search_vector", "search_vector", postgresql_using="gin"),
    )


class ProductTranslation(Base):
    __tablename__ = "product_translations"

    id: Mapped[bigint_pk]
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"))
    locale: Mapped[str] = mapped_column(String(10))  # uk, pl, en
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)
    meta_title: Mapped[Optional[str]] = mapped_column(String(255))
    meta_description: Mapped[Optional[str]] = mapped_column(String(320))

    __table_args__ = (
        Index("uq_product_translations_product_locale", "product_id", "locale", unique=True),
    )


class ProductVariant(Base):
    __tablename__ = "product_variants"

    id: Mapped[bigint_pk]
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"))
    sku: Mapped[str] = mapped_column(String(64), unique=True)
    size: Mapped[Optional[str]] = mapped_column(String(64))
    length_mm: Mapped[Optional[int]]
    weight: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 3))  # grams
    metal_type: Mapped[Optional[MetalType]] = mapped_column(pg_enum(MetalType, "metal_type"))
    metal_color: Mapped[Optional[MetalColor]] = mapped_column(pg_enum(MetalColor, "metal_color"))
    fineness: Mapped[Optional[int]]
    base_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))  # analytics / price_history only
    stock_quantity: Mapped[int] = mapped_column(server_default=text("0"))
    reserved_quantity: Mapped[int] = mapped_column(server_default=text("0"))

    __table_args__ = (
        CheckConstraint("stock_quantity >= 0", name="stock_non_negative"),
        CheckConstraint("reserved_quantity >= 0", name="reserved_non_negative"),
        CheckConstraint("base_price > 0", name="base_price_positive"),
        CheckConstraint(
            "fineness IS NULL OR fineness IN (375, 500, 585, 750, 875, 925, 958, 999)",
            name="fineness_allowed",
        ),
        Index("ix_product_variants_product_id", "product_id"),
    )


class VariantPrice(Base):
    __tablename__ = "variant_prices"

    id: Mapped[bigint_pk]
    variant_id: Mapped[int] = mapped_column(
        ForeignKey("product_variants.id", ondelete="CASCADE")
    )
    currency: Mapped[Currency] = mapped_column(pg_enum(Currency, "currency"))
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    sale_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    sale_starts_at: Mapped[Optional[datetime]]
    sale_ends_at: Mapped[Optional[datetime]]
    # D6: when true, a bulk price-recalculation job must not overwrite this row.
    is_manual_override: Mapped[bool] = mapped_column(server_default=text("false"))
    is_active: Mapped[bool] = mapped_column(server_default=text("true"))

    __table_args__ = (
        Index("uq_variant_prices_variant_currency", "variant_id", "currency", unique=True),
        CheckConstraint("price > 0", name="price_positive"),
        CheckConstraint("sale_price IS NULL OR sale_price > 0", name="sale_price_positive"),
    )


class PriceHistory(Base):
    """Source for the EU Omnibus rule: lowest price in the 30 days before a sale (PL)."""

    __tablename__ = "price_history"

    id: Mapped[bigint_pk]
    variant_id: Mapped[int] = mapped_column(
        ForeignKey("product_variants.id", ondelete="CASCADE")
    )
    currency: Mapped[Currency] = mapped_column(pg_enum(Currency, "currency"))
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    recorded_at: Mapped[datetime] = mapped_column(server_default=text("now()"))

    __table_args__ = (
        Index("ix_price_history_variant_currency_recorded", "variant_id", "currency", "recorded_at"),
        CheckConstraint("price > 0", name="price_positive"),
    )


class ProductImage(Base):
    __tablename__ = "product_images"

    id: Mapped[bigint_pk]
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"))
    variant_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("product_variants.id", ondelete="SET NULL")
    )
    storage_key: Mapped[str] = mapped_column(String(255))
    alt_text: Mapped[Optional[str]] = mapped_column(String(255))
    width: Mapped[Optional[int]]
    height: Mapped[Optional[int]]
    is_primary: Mapped[bool] = mapped_column(server_default=text("false"))
    sort_order: Mapped[int] = mapped_column(server_default=text("0"))

    __table_args__ = (Index("ix_product_images_product_id", "product_id"),)


class Gemstone(Base):
    __tablename__ = "gemstones"

    id: Mapped[int_pk]
    slug: Mapped[str] = mapped_column(String(50), unique=True)  # i18n key
    name: Mapped[str] = mapped_column(String(100))
    kind: Mapped[Optional[str]] = mapped_column(String(50))


class ProductGemstone(Base):
    __tablename__ = "product_gemstones"

    id: Mapped[bigint_pk]
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"))
    variant_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("product_variants.id", ondelete="CASCADE")
    )
    gemstone_id: Mapped[int] = mapped_column(ForeignKey("gemstones.id", ondelete="RESTRICT"))
    gemstone_type: Mapped[GemstoneType] = mapped_column(
        pg_enum(GemstoneType, "gemstone_type"), server_default="Natural"
    )
    quantity: Mapped[int] = mapped_column(server_default=text("1"))
    carat: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 3))
    cut_type: Mapped[Optional[str]] = mapped_column(String(30))
    color_grade: Mapped[Optional[str]] = mapped_column(String(10))
    clarity_grade: Mapped[Optional[str]] = mapped_column(String(10))
    setting_type: Mapped[Optional[str]] = mapped_column(String(30))
    certificate_number: Mapped[Optional[str]] = mapped_column(String(64))
    is_center_stone: Mapped[bool] = mapped_column(server_default=text("false"))

    __table_args__ = (
        CheckConstraint("quantity > 0", name="quantity_positive"),
        Index("ix_product_gemstones_product_id", "product_id"),
    )


class ProductEmbedding(Base):
    __tablename__ = "product_embeddings"

    product_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("products.id", ondelete="CASCADE"), primary_key=True
    )
    locale: Mapped[str] = mapped_column(String(10), primary_key=True)
    model_name: Mapped[str] = mapped_column(String(100), primary_key=True)
    embedding_version: Mapped[int] = mapped_column(Integer, server_default=text("1"))
    content_hash: Mapped[str] = mapped_column(String(64))  # SHA-256 of the canonical text
    embedding = mapped_column(Vector(EMBEDDING_DIM), nullable=False)
    updated_at: Mapped[updated_at_col]

    __table_args__ = (
        Index(
            "ix_product_embeddings_embedding_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )
