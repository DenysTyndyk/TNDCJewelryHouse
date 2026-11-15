from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.commerce import Cart
from app.repositories import cart_repository as repo
from app.repositories.catalog_repository import list_primary_images
from app.schemas.cart import MAX_LINE_QUANTITY, CartItemIn, CartLineOut, CartOut
from app.services.catalog_service import CURRENCY, _image_out
from app.models.enums import CartStatus


class CartError(Exception):
    pass


class VariantNotAvailableError(CartError):
    """Variant does not exist, is not published or has no active price -> 404."""


class CartItemNotFoundError(CartError):
    """Line does not exist in the caller's cart -> 404."""


class InsufficientStockError(CartError):
    """Requested quantity exceeds stock - reserved -> 409."""

    def __init__(self, available: int):
        super().__init__(f"Only {available} item(s) available")
        self.available = available

def _require_identity(user_id: int | None, session_token: str | None) -> None:
    if user_id is None and not session_token:
        raise ValueError("cart owner is require: user_id or session token")

def _check_quantity(quantity: int, available: int) -> None:
    limit = min(max(available,0), MAX_LINE_QUANTITY)
    if quantity > limit:
        raise InsufficientStockError(limit)

def _get_variant(db: Session,variant_id: int):
    variant = repo.get_purchasable_variant(db,variant_id,CURRENCY)
    if variant is None:
        raise VariantNotAvailableError(f"Variant {variant_id} is not available")
    return variant

def _build_cart_out(db: Session, cart: Cart | None, locale: str) -> CartOut:
    if cart is None:
        return CartOut()

    rows = repo.list_cart_lines(db, cart.id, locale, CURRENCY)
    images = {img.product_id: img for img in list_primary_images(db, list({r.product_id for r in rows}))}

    lines: list[CartLineOut] = []
    subtotal = Decimal("0.00")
    for r in rows:
        priced = r.unit_price is not None
        unit_price = r.unit_price if priced else (r.unit_price_at_add or Decimal("0.00"))
        line_total = unit_price * r.quantity
        if priced:
            subtotal += line_total
        img = images.get(r.product_id)
        lines.append(
            CartLineOut(
                id=r.id,
                variant_id=r.variant_id,
                product_id=r.product_id,
                product_slug=r.product_slug,
                name=r.name,
                sku=r.sku,
                size=r.size,
                image_url=_image_out(img).url if img else None,
                quantity=r.quantity,
                unit_price=unit_price,
                unit_price_at_add=r.unit_price_at_add,
                line_total=line_total,
                available=max(r.available, 0) if priced else 0,
            )
        )
    return CartOut(id=cart.id, items=lines, subtotal=subtotal, currency=CURRENCY)

def get_cart(db:Session, *, user_id: int | None, session_token: str | None, locale: str) -> CartOut:
    cart = repo.get_active_cart(db,user_id=user_id, session_token=session_token)
    return _build_cart_out(db,cart,locale)

def add_item(db: Session, data: CartItemIn, *, user_id: int | None, session_token: str | None, locale: str)-> CartOut:
    _require_identity(user_id, session_token)
    variant = _get_variant(db,data.variant_id)
    cart = repo.get_or_create_cart(db,user_id=user_id, session_token=session_token)

    item = repo.get_item_by_variant(db,cart.id,data.variant_id)
    if item is None:
        _check_quantity(data.quantity, variant.available)
        repo.add_item(db,cart_id=cart.id, variant_id=data.variant_id, quantity=data.quantity, unit_price=variant.unit_price)
    else:
        new_quantity = item.quantity + data.quantity
        _check_quantity(new_quantity, variant.available)
        repo.set_item_quantity(db,item,new_quantity)
    repo.touch_cart(db,cart)
    return _build_cart_out(db,cart,locale)

def update_item(
    db: Session, item_id: int, quantity: int, *, user_id: int | None, session_token: str | None, locale: str
) -> CartOut:
    cart, item = _get_own_item(db, item_id, user_id, session_token)
    variant = _get_variant(db, item.variant_id)
    _check_quantity(quantity, variant.available)
    repo.set_item_quantity(db, item, quantity)
    repo.touch_cart(db, cart)
    return _build_cart_out(db, cart, locale)


def remove_item(
    db: Session, item_id: int, *, user_id: int | None, session_token: str | None, locale: str
) -> CartOut:
    cart, item = _get_own_item(db, item_id, user_id, session_token)
    repo.delete_item(db, item)
    repo.touch_cart(db, cart)
    return _build_cart_out(db, cart, locale)


def _get_own_item(db: Session, item_id: int, user_id: int | None, session_token: str | None):
    cart = repo.get_active_cart(db, user_id=user_id, session_token=session_token)
    item = repo.get_item(db, cart.id, item_id) if cart else None
    if item is None:
        raise CartItemNotFoundError(f"Cart item {item_id} not found")
    return cart, item

def merge(db: Session, guest_token: str, user_id: int) -> None:
    guest = repo.get_active_cart(db,session_token=guest_token)
    if guest is None:
        return 
    guest_items = repo.list_items(db,guest.id)
    if guest_items:
        user_cart = repo.get_or_create_cart(db,user_id=user_id)
        user_items = {i.variant_id: i for i in repo.list_items(db,user_cart.id)}
        for g in guest_items:
            variant = repo.get_purchasable_variant(db, g.variant_id, CURRENCY)
            if variant is None:
                continue
            limit = min(max(variant.available,0), MAX_LINE_QUANTITY)
            existing = user_items.get(g.variant_id)
            if existing is not None:
                new_quantity = min(existing.quantity + g.quantity,limit)
                if new_quantity > existing.quantity:
                    repo.set_item_quantity(db,existing,new_quantity)
            else:
                quantity = min(g.quantity,limit)
                if quantity > 0:
                    repo.add_item(db,user_cart.id,g.variant_id,quantity,
                                  g.unit_price_at_add or variant.unit_price,
                                  )
        repo.touch_cart(db,user_cart)
    guest.session_token = None
    repo.set_cart_status(db, guest, CartStatus.Converted)