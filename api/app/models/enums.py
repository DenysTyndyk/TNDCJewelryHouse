import enum
from typing import Type

from sqlalchemy.dialects.postgresql import ENUM as PGEnum


class Role(str, enum.Enum):
    User = "User"
    Manager = "Manager"
    Admin = "Admin"


class UserStatus(str, enum.Enum):
    PendingVerification = "PendingVerification"
    Active = "Active"
    Suspended = "Suspended"
    Deactivated = "Deactivated"


class Currency(str, enum.Enum):
    UAH = "UAH"
    PLN = "PLN"
    USD = "USD"


class MetalType(str, enum.Enum):
    Gold = "Gold"
    Silver = "Silver"
    Platinum = "Platinum"


class MetalColor(str, enum.Enum):
    White = "White"
    Yellow = "Yellow"
    Rose = "Rose"
    Bicolor = "Bicolor"


class GemstoneType(str, enum.Enum):
    Natural = "Natural"
    LabGrown = "LabGrown"


class CartStatus(str, enum.Enum):
    Active = "Active"
    Abandoned = "Abandoned"
    Converted = "Converted"


class OrderStatus(str, enum.Enum):
    Pending = "Pending"
    Paid = "Paid"
    Processing = "Processing"
    Shipped = "Shipped"
    Delivered = "Delivered"
    Cancelled = "Cancelled"
    Returned = "Returned"


class PaymentStatus(str, enum.Enum):
    Pending = "Pending"
    Succeeded = "Succeeded"
    Failed = "Failed"
    Refunded = "Refunded"


class PaymentProvider(str, enum.Enum):
    LiqPay = "LiqPay"
    Monobank = "Monobank"
    Stripe = "Stripe"


class DeliveryProvider(str, enum.Enum):
    NovaPoshta = "NovaPoshta"
    UkrPoshta = "UkrPoshta"
    Courier = "Courier"


class EventType(str, enum.Enum):
    ProductView = "ProductView"
    CategoryView = "CategoryView"
    AddToCart = "AddToCart"
    RemoveFromCart = "RemoveFromCart"
    AddToFavorites = "AddToFavorites"
    Search = "Search"
    ClickRecommendation = "ClickRecommendation"
    Purchase = "Purchase"
    FilterApply = "FilterApply"


class SearchType(str, enum.Enum):
    Lexical = "Lexical"
    Semantic = "Semantic"
    Hybrid = "Hybrid"


def pg_enum(enum_cls: Type[enum.Enum], name: str) -> PGEnum:
    """Native PostgreSQL enum that is shared by several tables.

    create_type=False: the types are created once in migration 0001, so autogenerate
    never tries to CREATE TYPE the same enum twice.
    """
    return PGEnum(enum_cls, name=name, create_type=False)
