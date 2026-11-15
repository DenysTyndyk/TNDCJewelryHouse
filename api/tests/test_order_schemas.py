from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas.order import CheckoutIn, OrderItemOut

VALID = {
    "recipient_name": "Олена Коваль",
    "recipient_phone": "+380501234567",
    "customer_email": "olena@example.com",
    "shipping_method_id": 1,
    "shipping_city": "Київ",
    "provider_point_id": "12",
}


def test_valid_checkout_is_accepted_and_trimmed():
    data = CheckoutIn(**{**VALID, "recipient_name": "  Олена Коваль  "})
    assert data.recipient_name == "Олена Коваль"


def test_courier_address_instead_of_point_is_accepted():
    payload = {**VALID, "provider_point_id": None, "shipping_address_line": "вул. Хрещатик, 1"}
    assert CheckoutIn(**payload).shipping_address_line == "вул. Хрещатик, 1"


@pytest.mark.parametrize("override", [
    {"provider_point_id": None},                  
    {"recipient_phone": "0501234567"},            
    {"customer_email": "not-an-email"},
    {"shipping_method_id": 0},
    {"recipient_name": "   "},                    
    {"total": "1.00"},                             
])
def test_invalid_checkout_is_rejected(override):
    with pytest.raises(ValidationError):
        CheckoutIn(**{**VALID, **override})


def test_line_total_is_computed():
    item = OrderItemOut(variant_id=1, sku="R-1", product_name="Ring", quantity=3, unit_price=Decimal("1250.50"))
    assert item.model_dump()["line_total"] == Decimal("3751.50")
