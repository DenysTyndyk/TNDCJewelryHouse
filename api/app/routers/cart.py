import secrets
from dataclasses import dataclass

from fastapi import APIRouter, Depends, Header, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_optional_user
from app.schemas.cart import CartItemIn, CartItemUpdate, CartOut
from app.schemas.catalog import Locale
from app.services import cart_service
from app.services.catalog_service import resolve_locale
from app.services.cart_service import (
    CartItemNotFoundError,
    InsufficientStockError,
    VariantNotAvailableError,
)

CART_SESSION_HEADER = "X-Cart-Session"
x_cart_session: str | None = Header(
    default=None, alias=CART_SESSION_HEADER, min_length=16, max_length=128
),
router = APIRouter(prefix="/cart", tags=["cart"])


@dataclass
class CartOwner:
    user_id: int | None
    session_token: str | None
    locale: str


def get_cart_owner(
    response: Response,
    locale: Locale | None = None,
    accept_language: str | None = Header(default=None),
    x_cart_session: str | None = Header(default=None, min_length=16, max_length=128),
    user=Depends(get_optional_user),
) -> CartOwner:
    resolved_locale = resolve_locale(locale, accept_language)
    if user is not None:
        return CartOwner(user_id=user.id, session_token=None, locale=resolved_locale)

    token = x_cart_session or secrets.token_urlsafe(32)
    response.headers[CART_SESSION_HEADER] = token
    return CartOwner(user_id=None, session_token=token, locale=resolved_locale)

def _http_error(e: Exception) -> HTTPException:
    if isinstance(e, InsufficientStockError):
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"message": str(e), "available": e.available},
        )
    if isinstance(e, VariantNotAvailableError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variant not available")
    if isinstance(e, CartItemNotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")
    raise e


@router.get("", response_model=CartOut)
def get_cart(owner: CartOwner = Depends(get_cart_owner), db: Session = Depends(get_db)):
    return cart_service.get_cart(
        db, user_id=owner.user_id, session_token=owner.session_token, locale=owner.locale
    )


@router.post("/items", response_model=CartOut)
def add_item(
    data: CartItemIn,
    owner: CartOwner = Depends(get_cart_owner),
    db: Session = Depends(get_db),
):
    try:
        cart = cart_service.add_item(
            db, data, user_id=owner.user_id, session_token=owner.session_token, locale=owner.locale
        )
    except (InsufficientStockError, VariantNotAvailableError) as e:
        raise _http_error(e)
    db.commit()
    return cart


@router.patch("/items/{item_id}", response_model=CartOut)
def update_item(
    item_id: int,
    data: CartItemUpdate,
    owner: CartOwner = Depends(get_cart_owner),
    db: Session = Depends(get_db),
):
    try:
        cart = cart_service.update_item(
            db, item_id, data.quantity,
            user_id=owner.user_id, session_token=owner.session_token, locale=owner.locale,
        )
    except (InsufficientStockError, VariantNotAvailableError, CartItemNotFoundError) as e:
        raise _http_error(e)
    db.commit()
    return cart


@router.delete("/items/{item_id}", response_model=CartOut)
def remove_item(
    item_id: int,
    owner: CartOwner = Depends(get_cart_owner),
    db: Session = Depends(get_db),
):
    try:
        cart = cart_service.remove_item(
            db, item_id, user_id=owner.user_id, session_token=owner.session_token, locale=owner.locale
        )
    except CartItemNotFoundError as e:
        raise _http_error(e)
    db.commit()
    return cart