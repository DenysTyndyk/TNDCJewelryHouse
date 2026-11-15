"""Request/response models for the admin catalog API (Manager/Admin only)."""
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.enums import Currency, GemstoneType, MetalColor, MetalType
from app.schemas.catalog import Locale

SLUG_PATTERN = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"  # lowercase-kebab, safe for URLs


class _Out(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# --- categories ---

class CategoryTranslationIn(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str | None = None


class CategoryCreate(BaseModel):
    slug: str = Field(pattern=SLUG_PATTERN, max_length=120)
    parent_id: int | None = None
    is_active: bool = True
    sort_order: int = 0
    translations: dict[Locale, CategoryTranslationIn] = {}


class CategoryUpdate(BaseModel):
    slug: str | None = Field(default=None, pattern=SLUG_PATTERN, max_length=120)
    parent_id: int | None = None
    is_active: bool | None = None
    sort_order: int | None = None
    translations: dict[Locale, CategoryTranslationIn] | None = None


class CategoryAdminOut(_Out):
    id: int
    slug: str
    parent_id: int | None
    is_active: bool
    sort_order: int


# --- products ---

class ProductCreate(BaseModel):
    category_id: int
    slug: str = Field(pattern=SLUG_PATTERN, max_length=160)
    is_featured: bool = False
    published_at: datetime | None = None  # None = draft, not visible in the storefront


class ProductUpdate(BaseModel):
    category_id: int | None = None
    slug: str | None = Field(default=None, pattern=SLUG_PATTERN, max_length=160)
    is_featured: bool | None = None
    published_at: datetime | None = None  # send null explicitly to unpublish


class ProductAdminOut(_Out):
    id: int
    category_id: int
    slug: str
    is_featured: bool
    published_at: datetime | None


class ProductTranslationIn(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    meta_title: str | None = Field(default=None, max_length=255)
    meta_description: str | None = Field(default=None, max_length=320)


class ProductTranslationOut(ProductTranslationIn, _Out):
    locale: Locale


# --- variants and prices ---

class VariantCreate(BaseModel):
    sku: str = Field(min_length=1, max_length=64)
    size: str | None = Field(default=None, max_length=64)
    length_mm: int | None = Field(default=None, gt=0)
    weight: Decimal | None = Field(default=None, gt=0)
    metal_type: MetalType | None = None
    metal_color: MetalColor | None = None
    fineness: int | None = None  # allowed values are enforced by a DB check constraint
    base_price: Decimal = Field(gt=0)
    stock_quantity: int = Field(default=0, ge=0)


class VariantUpdate(BaseModel):
    sku: str | None = Field(default=None, min_length=1, max_length=64)
    size: str | None = Field(default=None, max_length=64)
    length_mm: int | None = Field(default=None, gt=0)
    weight: Decimal | None = Field(default=None, gt=0)
    metal_type: MetalType | None = None
    metal_color: MetalColor | None = None
    fineness: int | None = None
    base_price: Decimal | None = Field(default=None, gt=0)
    stock_quantity: int | None = Field(default=None, ge=0)


class VariantAdminOut(_Out):
    id: int
    product_id: int
    sku: str
    size: str | None
    length_mm: int | None
    weight: Decimal | None
    metal_type: MetalType | None
    metal_color: MetalColor | None
    fineness: int | None
    base_price: Decimal
    stock_quantity: int


class PriceIn(BaseModel):
    currency: Currency = Currency.UAH
    price: Decimal = Field(gt=0)
    sale_price: Decimal | None = Field(default=None, gt=0)
    sale_starts_at: datetime | None = None
    sale_ends_at: datetime | None = None
    # D6: a price set by hand is protected from bulk recalculation by default
    is_manual_override: bool = True
    is_active: bool = True

    @model_validator(mode="after")
    def check_sale(self) -> "PriceIn":
        if self.sale_price is not None and self.sale_price >= self.price:
            raise ValueError("sale_price must be lower than price")
        if self.sale_starts_at and self.sale_ends_at and self.sale_ends_at <= self.sale_starts_at:
            raise ValueError("sale_ends_at must be after sale_starts_at")
        return self


class PriceOut(_Out):
    variant_id: int
    currency: Currency
    price: Decimal
    sale_price: Decimal | None
    sale_starts_at: datetime | None
    sale_ends_at: datetime | None
    is_manual_override: bool
    is_active: bool


# --- gemstones ---

class ProductGemstoneIn(BaseModel):
    gemstone_id: int
    variant_id: int | None = None
    gemstone_type: GemstoneType = GemstoneType.Natural
    quantity: int = Field(default=1, gt=0)
    carat: Decimal | None = Field(default=None, gt=0)
    cut_type: str | None = Field(default=None, max_length=30)
    color_grade: str | None = Field(default=None, max_length=10)
    clarity_grade: str | None = Field(default=None, max_length=10)
    setting_type: str | None = Field(default=None, max_length=30)
    certificate_number: str | None = Field(default=None, max_length=64)
    is_center_stone: bool = False


class ProductGemstoneOut(ProductGemstoneIn, _Out):
    id: int
    product_id: int


# --- images ---

class ImageAdminOut(_Out):
    id: int
    product_id: int
    variant_id: int | None
    storage_key: str
    alt_text: str | None
    width: int | None
    height: int | None
    is_primary: bool
    sort_order: int
