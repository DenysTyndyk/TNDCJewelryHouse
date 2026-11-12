from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator
from app.models.enums import Currency, GemstoneType, MetalColor, MetalType

Locale = Literal["uk", "pl", "en"]
SortOrder = Literal["newest","price_asc","price_desc", "popular"]

class ImageOut(BaseModel):
    id: int
    url: str
    srcset: str | None = None
    alt_text: str | None = None
    width: int | None = None
    height: int | None = None
    is_primary: bool
    variant_id: int | None = None  

class VariantOut(BaseModel):
    id: int
    sku: str
    size: str | None = None
    length_mm: int | None = None
    weight: Decimal | None = None          
    metal_type: MetalType | None = None
    metal_color: MetalColor | None = None
    fineness: int | None = None
    price: Decimal                        
    sale_price: Decimal | None = None     
    currency: Currency
    in_stock: bool   

class GemstoneOut(BaseModel):
    slug: str                      
    name: str                      
    gemstone_type: GemstoneType
    quantity: int
    carat: Decimal | None = None
    cut_type: str | None = None
    color_grade: str | None = None
    clarity_grade: str | None = None
    is_center_stone: bool
    variant_id: int | None = None  

class CategoryNode(BaseModel):
    id: int
    slug: str
    name: str
    description: str | None = None
    children: list["CategoryNode"] = []

class ProductListItem(BaseModel):
    id: int
    slug: str
    name: str
    category_slug: str
    price_from: Decimal            
    currency: Currency
    has_sale: bool
    in_stock: bool                
    is_featured: bool
    image: ImageOut | None = None  

class ProductDetail(BaseModel):
    id: int
    slug: str
    name: str
    description: str | None = None
    meta_title: str | None = None
    meta_description: str | None = None
    category: CategoryNode         
    variants: list[VariantOut]
    images: list[ImageOut]
    gemstones: list[GemstoneOut] = []


class ProductPage(BaseModel):
    items: list[ProductListItem]
    next_cursor: str | None = None  

class ProductFilter(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category: str | None = None    
    metal: MetalType | None = None
    color: MetalColor | None = None
    fineness: int | None = None    
    price_min: Decimal | None = Field(default=None, ge=0)
    price_max: Decimal | None = Field(default=None, ge=0)
    gemstone: str | None = None    
    in_stock: bool | None = None
    sort: SortOrder = "newest"
    cursor: str | None = None
    limit: int = Field(default=24, ge=1, le=100)
    locale: Locale | None = None 

    @model_validator(mode="after")
    def check_price_range(self) -> "ProductFilter":
        if (
            self.price_min is not None
            and self.price_max is not None
            and self.price_min > self.price_max
        ):
            raise ValueError("price_min must be <= price_max")
        return self
