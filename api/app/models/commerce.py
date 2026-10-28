from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import CheckConstraint, ForeignKey, Index, Numeric, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, bigint_pk, created_at_col, updated_at_col
from app.models.enums import (
    CartStatus,
    Currency,
    OrderStatus,
    PaymentProvider,
    PaymentStatus,
    pg_enum,
)


class Cart(Base):
    __tablename__ = "carts"

    id: Mapped[bigint_pk]
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    session_token: Mapped[Optional[str]] = mapped_column(String(128), unique=True)
    status: Mapped[CartStatus] = mapped_column(
        pg_enum(CartStatus, "cart_status"), server_default="Active"
    )
    last_activity_at: Mapped[Optional[datetime]]
    created_at: Mapped[created_at_col]
    updated_at: Mapped[updated_at_col]

    __table_args__ = (Index("ix_carts_user_id_status", "user_id", "status"),)


class CartItem(Base):
    __tablename__ = "cart_items"

    id: Mapped[bigint_pk]
    cart_id: Mapped[int] = mapped_column(ForeignKey("carts.id", ondelete="CASCADE"))
    variant_id: Mapped[int] = mapped_column(
        ForeignKey("product_variants.id", ondelete="CASCADE")
    )
    quantity: Mapped[int]
    unit_price_at_add: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))

    __table_args__ = (
        Index("uq_cart_items_cart_variant", "cart_id", "variant_id", unique=True),
        CheckConstraint("quantity > 0", name="quantity_positive"),
    )


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[bigint_pk]
    order_number: Mapped[str] = mapped_column(String(32), unique=True)  # TNDC-2026-00145
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    shipping_method_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("shipping_methods.id", ondelete="SET NULL")
    )
    status: Mapped[OrderStatus] = mapped_column(
        pg_enum(OrderStatus, "order_status"), server_default="Pending"
    )
    currency: Mapped[Currency] = mapped_column(pg_enum(Currency, "currency"))
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), server_default=text("0"))
    shipping_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), server_default=text("0"))
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    exchange_rate_used: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 6))
    locale: Mapped[Optional[str]] = mapped_column(String(10))
    # Links a guest order to its pre-purchase events (used by the M9 evaluation).
    session_token: Mapped[Optional[str]] = mapped_column(String(128))
    recommendation_influenced: Mapped[bool] = mapped_column(server_default=text("false"))

    # Checkout snapshot: independent of later profile/address edits.
    recipient_name: Mapped[str] = mapped_column(String(200))
    recipient_phone: Mapped[str] = mapped_column(String(32))
    customer_email: Mapped[Optional[str]] = mapped_column(String(255))
    shipping_country: Mapped[str] = mapped_column(String(2))
    shipping_city: Mapped[Optional[str]] = mapped_column(String(100))
    shipping_address_line: Mapped[Optional[str]] = mapped_column(String(255))
    provider_point_id: Mapped[Optional[str]] = mapped_column(String(64))
    tracking_number: Mapped[Optional[str]] = mapped_column(String(64))
    customer_note: Mapped[Optional[str]] = mapped_column(Text)

    created_at: Mapped[created_at_col]
    paid_at: Mapped[Optional[datetime]]
    shipped_at: Mapped[Optional[datetime]]
    delivered_at: Mapped[Optional[datetime]]
    cancelled_at: Mapped[Optional[datetime]]

    __table_args__ = (
        CheckConstraint("subtotal >= 0", name="subtotal_non_negative"),
        CheckConstraint("total >= 0", name="total_non_negative"),
        Index("ix_orders_user_id", "user_id"),
        Index("ix_orders_session_token", "session_token"),
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[bigint_pk]
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="RESTRICT"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="RESTRICT"))
    variant_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("product_variants.id", ondelete="SET NULL")
    )
    sku: Mapped[str] = mapped_column(String(64))
    quantity: Mapped[int]
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    product_name: Mapped[str] = mapped_column(String(255))  # snapshot at purchase
    variant_snapshot: Mapped[Optional[dict]] = mapped_column(JSONB)

    __table_args__ = (
        CheckConstraint("quantity > 0", name="quantity_positive"),
        CheckConstraint("unit_price >= 0", name="unit_price_non_negative"),
        Index("ix_order_items_order_id", "order_id"),
    )


class Payment(Base):
    """No card numbers or CVV here, ever (PCI-DSS): only provider references."""

    __tablename__ = "payments"

    id: Mapped[bigint_pk]
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="RESTRICT"))
    provider: Mapped[PaymentProvider] = mapped_column(
        pg_enum(PaymentProvider, "payment_provider")
    )
    status: Mapped[PaymentStatus] = mapped_column(
        pg_enum(PaymentStatus, "payment_status"), server_default="Pending"
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    currency: Mapped[Currency] = mapped_column(pg_enum(Currency, "currency"))
    external_id: Mapped[Optional[str]] = mapped_column(String(128))
    idempotency_key: Mapped[str] = mapped_column(String(128), unique=True)
    gateway_response: Mapped[Optional[dict]] = mapped_column(JSONB)
    created_at: Mapped[created_at_col]
    paid_at: Mapped[Optional[datetime]]

    __table_args__ = (
        CheckConstraint("amount > 0", name="amount_positive"),
        Index("ix_payments_order_id", "order_id"),
    )


class Favorite(Base):
    __tablename__ = "favorites"

    id: Mapped[bigint_pk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"))
    created_at: Mapped[created_at_col]

    __table_args__ = (
        Index("uq_favorites_user_product", "user_id", "product_id", unique=True),
    )
