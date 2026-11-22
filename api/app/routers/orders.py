import logging

from fastapi import APIRouter, Depends, Header, HTTPException, Path, Request, status
from app.core.limiter import limiter
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.routers.cart import CartOwner, get_cart_owner
from app.schemas.order import CheckoutIn, OrderOut, ShippingMethodOut
from app.services import order_service,telemetry_service
from app.services.telemetry_service import TRACKING_CONSENT_HEADER
from app.services.order_service import (
    DeliveryDetailsError,
    EmptyCartError,
    InvalidTransitionError,
    OrderNotFoundError,
    OutOfStockError,
    ShippingMethodNotFoundError,
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["orders"])

OrderNumber = Path(max_length=32)


@router.get("/shipping-methods", response_model=list[ShippingMethodOut])
def list_shipping_methods(db: Session = Depends(get_db)):
    """Active delivery options for checkout, cheapest first."""
    return order_service.list_shipping_methods(db)


@router.post("/orders", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def create_order(
    request: Request,
    data: CheckoutIn,
    owner: CartOwner = Depends(get_cart_owner),
    x_tracking_consent: str | None = Header(default=None, alias=TRACKING_CONSENT_HEADER, max_length=16),
    db: Session = Depends(get_db),
):
    """Check out the caller's cart. Guests send X-Cart-Session (and X-Tracking-Consent if they agreed)."""
    try:
        out = order_service.checkout(
            db, data, user_id=owner.user_id, session_token=owner.session_token, locale=owner.locale,
            track_purchase=telemetry_service.tracking_allowed(db, owner.user_id, x_tracking_consent),
        )
    except EmptyCartError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except (ShippingMethodNotFoundError, DeliveryDetailsError) as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except OutOfStockError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"message": str(e), "items": e.shortages},
        )
    db.commit()

    try:
        order_service.send_order_created_email(out, owner.locale)
    except Exception:
        logger.exception("Order-created email failed for %s", out.order_number)
    return out


@router.get("/orders", response_model=list[OrderOut])
def list_orders(owner: CartOwner = Depends(get_cart_owner), db: Session = Depends(get_db)):
    """The caller's orders, newest first (max 50, without items)."""
    return order_service.list_orders(db, user_id=owner.user_id, session_token=owner.session_token)


@router.get("/orders/{order_number}", response_model=OrderOut)
def get_order(
    order_number: str = OrderNumber,
    owner: CartOwner = Depends(get_cart_owner),
    db: Session = Depends(get_db),
):
    try:
        return order_service.get_order(
            db, order_number, user_id=owner.user_id, session_token=owner.session_token
        )
    except OrderNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

@router.post("/orders/{order_number}/cancel", response_model=OrderOut)
def cancel_order(
    order_number: str = OrderNumber,
    owner: CartOwner = Depends(get_cart_owner),
    db: Session = Depends(get_db),
):
    try:
        out = order_service.cancel(
            db, order_number, user_id=owner.user_id, session_token=owner.session_token
        )
    except OrderNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    except InvalidTransitionError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    db.commit()
    return out
