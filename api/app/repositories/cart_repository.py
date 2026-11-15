from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import and_, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, aliased

from app.models.catalog import Product, ProductTranslation, ProductVariant, VariantPrice
from app.models.commerce import Cart, CartItem
from app.models.enums import CartStatus, Currency
from app.repositories.catalog_repository import (
    AVAILABLE,
    DEFAULT_LOCALE,
    EFFECTIVE_PRICE,
    IS_PUBLISHED,
)

def get_active_cart(db: Session, * , user_id: int | None=None, session_token: str | None=None) -> Cart | None:
    stmt = select(Cart).where(Cart.status == CartStatus.Active)
    if user_id is not None:
        stmt = stmt.where(Cart.user_id == user_id)
    elif session_token:
        stmt = stmt.where(Cart.session_token == session_token, Cart.user_id.is_(None))
    else:
        return None
    return db.scalar(stmt)

def get_or_create_cart(db: Session, *, user_id: int | None=None, session_token: str | None=None) -> Cart:
    cart = get_active_cart(db,user_id=user_id,session_token=session_token)
    if cart is not None:
        return cart
    try:
        with db.begin_nested():
            cart = Cart(user_id=user_id,session_token = None if user_id is not None else session_token,last_activity_at=datetime.now(timezone.utc),
                        )
            db.add(cart)
            db.flush()
        return cart
    except IntegrityError:
        cart = get_active_cart(db,user_id=user_id, session_token=session_token)
        if cart is None:
            raise
        return cart

def touch_cart(db: Session, cart: Cart) -> None:
    cart.last_activity_at = datetime.now(timezone.utc)
    db.flush()

def set_cart_status(db: Session, cart: Cart, status: CartStatus) -> None:
    cart.status = status
    db.flush()


def get_item(db: Session,cart_id: int, item_id: int) -> CartItem | None:
    return db.scalar(
        select(CartItem).where(CartItem.id == item_id, CartItem.cart_id == cart_id)
    )

def get_item_by_variant(db:Session, cart_id: int, variant_id: int) -> CartItem | None:
    return db.scalar(
        select(CartItem).where(CartItem.cart_id == cart_id, CartItem.variant_id==variant_id)
    )

def list_items(db: Session, cart_id: int) -> list[CartItem]: 
    return list(db.scalars(select(CartItem).where(CartItem.cart_id == cart_id).order_by(CartItem.id)))

def add_item(db: Session, cart_id: int, variant_id: int, quantity: int, unit_price: Decimal)-> CartItem: 
    item = CartItem(cart_id=cart_id, variant_id=variant_id, quantity=quantity, unit_price_at_add= unit_price)
    db.add(item)
    db.flush()
    return item

def set_item_quantity(db: Session, item: CartItem, quantity: int) -> None:
    item.quantity = quantity
    db.flush()

def delete_item(db: Session, item: CartItem)-> None:
    db.delete(item)
    db.flush()

def get_purchasable_variant(db: Session, variant_id: int, currency: Currency):
    stmt = (
        select(
            ProductVariant.id,
            ProductVariant.product_id,
            EFFECTIVE_PRICE.label("unit_price"),
            AVAILABLE.label("available"),
        )
        .join(Product, Product.id == ProductVariant.product_id)
        .join(
            VariantPrice,
            and_(
                VariantPrice.variant_id == ProductVariant.id,
                VariantPrice.currency == currency,
                VariantPrice.is_active,
            ),
        )
        .where(ProductVariant.id == variant_id, IS_PUBLISHED)
    )
    return db.execute(stmt).first()

def list_cart_lines(db: Session, cart_id: int, locale: str, currency: Currency):
    tr = aliased(ProductTranslation)
    tr_default = aliased(ProductTranslation)
    stmt = (
        select(
            CartItem.id,
            CartItem.variant_id,
            CartItem.quantity,
            CartItem.unit_price_at_add,
            ProductVariant.sku,
            ProductVariant.size,
            Product.id.label("product_id"),
            Product.slug.label("product_slug"),
            func.coalesce(tr.name, tr_default.name, Product.slug).label("name"),
            EFFECTIVE_PRICE.label("unit_price"),  # None if the price was removed
            AVAILABLE.label("available"),
        )
        .join(ProductVariant, ProductVariant.id == CartItem.variant_id)
        .join(Product, Product.id == ProductVariant.product_id)
        .outerjoin(tr, and_(tr.product_id == Product.id, tr.locale == locale))
        .outerjoin(tr_default, and_(tr_default.product_id == Product.id, tr_default.locale == DEFAULT_LOCALE))
        .outerjoin(
            VariantPrice,
            and_(
                VariantPrice.variant_id == ProductVariant.id,
                VariantPrice.currency == currency,
                VariantPrice.is_active,
            ),
        )
        .where(CartItem.cart_id == cart_id)
        .order_by(CartItem.id)
    )
    return db.execute(stmt).all()