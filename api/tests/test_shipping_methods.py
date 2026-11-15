from decimal import Decimal

from app.models.enums import Currency, DeliveryProvider
from app.models.logistics import ShippingMethod


def _method(db, name, cost, is_active=True, free_from=None):
    method = ShippingMethod(
        provider=DeliveryProvider.NovaPoshta,
        name=name,
        cost=Decimal(cost),
        currency=Currency.UAH,
        free_from_amount=Decimal(free_from) if free_from else None,
        is_active=is_active,
    )
    db.add(method)
    db.flush()
    return method


def test_lists_only_active_methods_cheapest_first(client, db_session):
    expensive = _method(db_session, "Courier", "150.00")
    cheap = _method(db_session, "Branch", "80.00", free_from="3000.00")
    _method(db_session, "Disabled", "10.00", is_active=False)

    res = client.get("/shipping-methods")

    assert res.status_code == 200
    body = res.json()
    ids = [m["id"] for m in body]
    assert ids.index(cheap.id) < ids.index(expensive.id)
    assert "Disabled" not in [m["name"] for m in body]

    branch = next(m for m in body if m["id"] == cheap.id)
    assert branch["cost"] == "80.00"
    assert branch["free_from_amount"] == "3000.00"
    assert "is_active" not in branch
