from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import Currency

MAX_LINE_QUANTITY = 99

class CartItemIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    variant_id: int = Field(gt=0)
    quantity: int = Field(default=1, ge=1, le=MAX_LINE_QUANTITY)

class CartItemUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    quantity: int = Field(ge=1, le=MAX_LINE_QUANTITY)

class CartLineOut(BaseModel):
    id: int
    variant_id: int
    product_slug: str
    name: str
    sku: str
    size: str | None = None
    image_url: str | None = None
    quantity: int
    unit_price: Decimal        
    unit_price_at_add: Decimal | None = None
    line_total: Decimal          
    available: int

class CartOut(BaseModel):
    id: int | None = None
    items: list[CartLineOut] = []
    subtotal: Decimal = Decimal("0.00")
    currency: Currency = Currency.UAH