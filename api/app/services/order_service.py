"""Order business logic: shipping methods, checkout, cancellation (T4.6)."""
from decimal import Decimal

from sqlalchemy.orm import Session
from sqlalchemy import and_, func, select

from app.models.commerce import Order, OrderItem
from app.models.enums import CartStatus, DeliveryProvider, OrderStatus,EventType
from app.models.logistics import ShippingMethod
from app.repositories import cart_repository,telemetry_repository
from app.repositories import order_repository as repo
from app.schemas.order import CheckoutIn, OrderItemOut, OrderOut
from app.services.catalog_service import CURRENCY
from app.core.config import settings
from app.core.email import send_email
from datetime import datetime, timezone
SHIPPING_COUNTRY = "UA"  
ORDERS_PAGE_LIMIT = 50
ALLOWED_TRANSITIONS: dict[OrderStatus, frozenset[OrderStatus]] = {
    OrderStatus.Pending: frozenset({OrderStatus.Paid, OrderStatus.Cancelled}),
    OrderStatus.Paid: frozenset({OrderStatus.Processing}),
    OrderStatus.Processing: frozenset({OrderStatus.Shipped}),
    OrderStatus.Shipped: frozenset({OrderStatus.Delivered}),
    OrderStatus.Delivered: frozenset({OrderStatus.Returned}),
    OrderStatus.Cancelled: frozenset(),
    OrderStatus.Returned: frozenset(),
}
POINT_PROVIDERS = {DeliveryProvider.NovaPoshta, DeliveryProvider.UkrPoshta}
_ORDER_CREATED_TEXT = {
    "uk": {"subject": "Замовлення {number} створено", "intro": "Дякуємо! Ваше замовлення {number} прийнято.",
           "shipping": "Доставка", "total": "Разом", "link": "Статус замовлення"},
    "pl": {"subject": "Zamówienie {number} zostało utworzone", "intro": "Dziękujemy! Przyjęliśmy zamówienie {number}.",
           "shipping": "Dostawa", "total": "Razem", "link": "Status zamówienia"},
    "en": {"subject": "Order {number} created", "intro": "Thank you! Your order {number} has been received.",
           "shipping": "Shipping", "total": "Total", "link": "Order status"},
}


class CheckoutError(Exception):
    pass

class OrderNotFoundError(Exception):
    """Order does not exist or belongs to someone else -> 404."""

class InvalidTransitionError(Exception):
    """Status change not in ALLOWED_TRANSITIONS -> 409."""

    def __init__(self, current: OrderStatus, target: OrderStatus):
        super().__init__(f"Cannot change order status from {current.value} to {target.value}")

class EmptyCartError(CheckoutError):
    """No active cart, or it has no lines -> 400."""


class ShippingMethodNotFoundError(CheckoutError):
    """Unknown or inactive shipping method -> 422."""


class DeliveryDetailsError(CheckoutError):
    """Branch/address missing for the chosen provider -> 422."""


class OutOfStockError(CheckoutError):
    """Some lines exceed stock - reserved -> 409."""

    def __init__(self, shortages: list[dict]):
        super().__init__("Some items are no longer available")
        self.shortages = shortages


def list_shipping_methods(db: Session) -> list[ShippingMethod]:
    return repo.list_active_shipping_methods(db)


def _shipping_amount(method: ShippingMethod, subtotal: Decimal) -> Decimal:
    if method.free_from_amount is not None and subtotal >= method.free_from_amount:
        return Decimal("0.00")
    return method.cost


def _check_delivery_details(method: ShippingMethod, data: CheckoutIn) -> None:
    if method.provider in POINT_PROVIDERS and not data.provider_point_id:
        raise DeliveryDetailsError("provider_point_id is required for this shipping method")
    if method.provider == DeliveryProvider.Courier and not data.shipping_address_line:
        raise DeliveryDetailsError("shipping_address_line is required for courier delivery")

def _transition(order: Order, target: OrderStatus) -> None:
    if target not in ALLOWED_TRANSITIONS[order.status]:
        raise InvalidTransitionError(order.status, target)
    order.status = target


def checkout(
    db: Session,
    data: CheckoutIn,
    *,
    user_id: int | None,
    session_token: str | None,
    locale: str,
    track_purchase: bool = False,
) -> OrderOut:
    cart = cart_repository.get_active_cart(db, user_id=user_id, session_token=session_token)
    if cart is None:
        raise EmptyCartError("Cart is empty")
    db.refresh(cart, with_for_update=True)
    if cart.status != CartStatus.Active:
        raise EmptyCartError("Cart is empty")

    lines = cart_repository.list_cart_lines(db, cart.id, locale, CURRENCY)
    if not lines:
        raise EmptyCartError("Cart is empty")

    method = repo.get_active_shipping_method(db, data.shipping_method_id)
    if method is None:
        raise ShippingMethodNotFoundError("Shipping method not available")
    _check_delivery_details(method, data)

    variants = repo.lock_purchasable_variants(db, sorted({line.variant_id for line in lines}))

    shortages = []
    for line in lines:
        variant = variants.get(line.variant_id)
        if variant is None or line.unit_price is None:
            available = 0  
        else:
            available = max(variant.stock_quantity - variant.reserved_quantity, 0)
        if line.quantity > available:
            shortages.append({
                "variant_id": line.variant_id,
                "sku": line.sku,
                "requested": line.quantity,
                "available": available,
            })
    if shortages:
        raise OutOfStockError(shortages)

    subtotal = sum((line.unit_price * line.quantity for line in lines), Decimal("0.00"))
    shipping_amount = _shipping_amount(method, subtotal)

    order = Order(
        order_number=repo.next_order_number(db),
        user_id=user_id,
        session_token=session_token,
        shipping_method_id=method.id,
        currency=CURRENCY,
        subtotal=subtotal,
        shipping_amount=shipping_amount,
        total=subtotal + shipping_amount,
        locale=locale,
        recipient_name=data.recipient_name,
        recipient_phone=data.recipient_phone,
        customer_email=data.customer_email,
        shipping_country=SHIPPING_COUNTRY,
        shipping_city=data.shipping_city,
        shipping_address_line=data.shipping_address_line,
        provider_point_id=data.provider_point_id,
        customer_note=data.customer_note,
    )
    db.add(order)
    db.flush() 

    items = []
    for line in lines:
        variant = variants[line.variant_id]
        item = OrderItem(
            order_id=order.id,
            product_id=line.product_id,
            variant_id=variant.id,
            sku=line.sku,
            quantity=line.quantity,
            unit_price=line.unit_price,
            product_name=line.name,
            variant_snapshot={
                "size": variant.size,
                "metal_type": variant.metal_type.value if variant.metal_type else None,
                "metal_color": variant.metal_color.value if variant.metal_color else None,
                "fineness": variant.fineness,
            },
        )
        db.add(item)
        items.append(item)
        variant.reserved_quantity += line.quantity
    if track_purchase:
        telemetry_repository.bulk_insert_events(db, [
            {
                "user_id": user_id,
                "session_token": session_token,
                "event_type": EventType.Purchase,
                "product_id": item.product_id,
                "variant_id": item.variant_id,
                "event_metadata": {"quantity": item.quantity},
            }
            for item in items
        ])

    cart.session_token = None
    cart_repository.set_cart_status(db, cart, CartStatus.Converted)

    out = OrderOut.model_validate(order)
    out.items = [OrderItemOut.model_validate(i) for i in items]
    return out

def send_order_created_email(order: OrderOut, locale: str) -> None:
    if not order.customer_email:
        return
    text = _ORDER_CREATED_TEXT.get(locale, _ORDER_CREATED_TEXT["uk"])
    currency = order.currency.value
    lines = [f"- {i.product_name} ({i.sku}) × {i.quantity} = {i.line_total} {currency}" for i in order.items]
    body = "\n".join([
        text["intro"].format(number=order.order_number),
        "",
        *lines,
        "",
        f"{text['shipping']}: {order.shipping_amount} {currency}",
        f"{text['total']}: {order.total} {currency}",
        "",
        f"{text['link']}: {settings.frontend_base_url}/orders/{order.order_number}",
    ])
    send_email(order.customer_email, text["subject"].format(number=order.order_number), body)

def _owned_by(user_id: int | None, session_token: str | None):
    if user_id is not None:
        return Order.user_id == user_id
    return and_(Order.user_id.is_(None), Order.session_token == session_token)


def list_orders(db: Session, *, user_id: int | None, session_token: str | None, limit: int) -> list[Order]:
    stmt = (
        select(Order)
        .where(_owned_by(user_id, session_token))
        .order_by(Order.created_at.desc(), Order.id.desc())
        .limit(limit)
    )
    return list(db.scalars(stmt))


def get_order(db: Session, order_number: str, *, user_id: int | None, session_token: str | None) -> Order | None:
    return db.scalar(
        select(Order).where(Order.order_number == order_number, _owned_by(user_id, session_token))
    )


def list_order_items(db: Session, order_id: int) -> list[OrderItem]:
    return list(db.scalars(select(OrderItem).where(OrderItem.order_id == order_id).order_by(OrderItem.id)))

def list_orders(db: Session, *, user_id: int | None, session_token: str | None) -> list[OrderOut]:
    orders = repo.list_orders(db, user_id=user_id, session_token=session_token, limit=ORDERS_PAGE_LIMIT)
    return [OrderOut.model_validate(o) for o in orders]  


def _order_out(db: Session, order: Order) -> OrderOut:
    out = OrderOut.model_validate(order)
    out.items = [OrderItemOut.model_validate(i) for i in repo.list_order_items(db, order.id)]
    return out


def get_order(db: Session, order_number: str, *, user_id: int | None, session_token: str | None) -> OrderOut:
    order = repo.get_order(db, order_number, user_id=user_id, session_token=session_token)
    if order is None:
        raise OrderNotFoundError(order_number)
    return _order_out(db, order)

def cancel(db: Session, order_number: str, *, user_id: int | None, session_token: str | None) -> OrderOut:
    order = repo.get_order(
        db, order_number, user_id=user_id, session_token=session_token, for_update=True
    )
    if order is None:
        raise OrderNotFoundError(order_number)
    _transition(order, OrderStatus.Cancelled)

    items = repo.list_order_items(db, order.id)
    variant_ids = sorted({i.variant_id for i in items if i.variant_id is not None})
    variants = repo.lock_variants(db, variant_ids)
    for item in items:
        variant = variants.get(item.variant_id)
        if variant is not None:
            variant.reserved_quantity -= item.quantity

    order.cancelled_at = datetime.now(timezone.utc)
    db.flush()
    return _order_out(db, order)
