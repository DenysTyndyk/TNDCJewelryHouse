from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, computed_field, model_validator

from app.models.enums import Currency, DeliveryProvider, OrderStatus
from app.schemas.auth import PHONE_PATTERN

class ShippingMethodOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    provider: DeliveryProvider
    name: str
    cost: Decimal
    currency: Currency
    free_from_amount: Decimal | None = None
    delivery_days_min: int | None = None
    delivery_days_max: int | None = None

class CheckoutIn(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    recipient_name: str = Field(min_length=2, max_length=200)
    recipient_phone: str = Field(pattern=PHONE_PATTERN, max_length=32)
    customer_email: EmailStr = Field(max_length=255)
    shipping_method_id: int = Field(gt=0)
    shipping_city: str = Field(min_length=2, max_length=100)
    provider_point_id: str | None = Field(default=None, min_length=1, max_length=64)
    shipping_address_line: str | None = Field(default=None, min_length=3, max_length=255)
    customer_note: str | None = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def _point_or_address(self):
        if not self.provider_point_id and not self.shipping_address_line:
            raise ValueError("Either provider_point_id or shipping_address_line is required")
        return self

class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    variant_id: int | None  
    sku: str
    product_name: str
    quantity: int
    unit_price: Decimal

    @computed_field
    @property
    def line_total(self) -> Decimal:
        return self.unit_price * self.quantity

class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    order_number: str
    status: OrderStatus
    currency: Currency
    subtotal: Decimal
    discount_amount: Decimal
    shipping_amount: Decimal
    total: Decimal

    shipping_method_id: int | None
    recipient_name: str
    recipient_phone: str
    customer_email: str | None
    shipping_city: str | None
    shipping_address_line: str | None
    provider_point_id: str | None
    customer_note: str | None
    tracking_number: str | None

    created_at: datetime
    paid_at: datetime | None
    cancelled_at: datetime | None

    items: list[OrderItemOut] = []

