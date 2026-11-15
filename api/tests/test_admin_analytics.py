"""Admin analytics: role guard, per-day counts, top products, query limits (M5 T5)."""
from datetime import datetime
from zoneinfo import ZoneInfo

from app.models.enums import EventType, Role
from app.models.telemetry import UserEvent
from tests.test_admin_catalog import _auth
from tests.test_checkout import _setup


def _today_count(rows, event_type):
    # Reports group by Kyiv calendar day, so "today" must be Kyiv's too.
    today = datetime.now(ZoneInfo("Europe/Kyiv")).date().isoformat()
    return sum(r["count"] for r in rows if r["day"] == today and r["event_type"] == event_type)


def test_requires_admin_role(client, db_session):
    assert client.get("/admin/analytics/events").status_code == 401
    assert client.get("/admin/analytics/events", headers=_auth(db_session, Role.User)).status_code == 403


def test_events_by_day_counts_new_events(client, db_session):
    h = _auth(db_session, Role.Manager)
    before = _today_count(client.get("/admin/analytics/events", headers=h).json(), "CategoryView")
    db_session.add_all([UserEvent(event_type=EventType.CategoryView) for _ in range(2)])
    db_session.flush()
    after = _today_count(client.get("/admin/analytics/events", headers=h).json(), "CategoryView")
    assert after - before == 2


def test_top_products_counts_and_orders(client, db_session):
    h = _auth(db_session, Role.Admin)
    variant, _, _ = _setup(db_session)
    db_session.add_all(
        [UserEvent(event_type=EventType.ProductView, product_id=variant.product_id) for _ in range(3)]
    )
    db_session.flush()

    rows = client.get("/admin/analytics/top-products?limit=100", headers=h).json()
    mine = next(r for r in rows if r["product_id"] == variant.product_id)
    assert mine["count"] >= 3 and mine["slug"] == "checkout-test-ring"
    assert [r["count"] for r in rows] == sorted((r["count"] for r in rows), reverse=True)


def test_query_limits_validated(client, db_session):
    h = _auth(db_session, Role.Admin)
    assert client.get("/admin/analytics/events?days=0", headers=h).status_code == 422
    assert client.get("/admin/analytics/events?days=366", headers=h).status_code == 422
    assert client.get("/admin/analytics/top-products?limit=101", headers=h).status_code == 422
    assert client.get("/admin/analytics/top-products?event_type=Hack", headers=h).status_code == 422
