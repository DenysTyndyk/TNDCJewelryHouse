from decimal import Decimal
from typing import Optional

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, Numeric, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, bigint_pk, created_at_col, int_pk
from app.models.enums import Currency, DeliveryProvider, pg_enum


class ShippingMethod(Base):
    __tablename__ = "shipping_methods"

    id: Mapped[int_pk]
    provider: Mapped[DeliveryProvider] = mapped_column(
        pg_enum(DeliveryProvider, "delivery_provider")
    )
    name: Mapped[str] = mapped_column(String(100))
    cost: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    currency: Mapped[Currency] = mapped_column(pg_enum(Currency, "currency"))
    free_from_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    delivery_days_min: Mapped[Optional[int]] = mapped_column(Integer)
    delivery_days_max: Mapped[Optional[int]] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(server_default=text("true"))

    __table_args__ = (
        CheckConstraint("cost >= 0", name="cost_non_negative"),
    )


class UserAddress(Base):
    __tablename__ = "user_addresses"

    id: Mapped[bigint_pk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    # Same widths as orders.recipient_* so checkout can copy without truncation.
    recipient_name: Mapped[str] = mapped_column(String(200))
    recipient_phone: Mapped[str] = mapped_column(String(32))
    delivery_provider: Mapped[DeliveryProvider] = mapped_column(
        pg_enum(DeliveryProvider, "delivery_provider")
    )
    provider_point_id: Mapped[Optional[str]] = mapped_column(String(64))
    country_code: Mapped[str] = mapped_column(String(2))
    is_default: Mapped[bool] = mapped_column(server_default=text("false"))
    city: Mapped[Optional[str]] = mapped_column(String(100))
    postal_code: Mapped[Optional[str]] = mapped_column(String(16))
    line1: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[created_at_col]

    __table_args__ = (Index("ix_user_addresses_user_id", "user_id"),)
