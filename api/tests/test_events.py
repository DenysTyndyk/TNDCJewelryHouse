from decimal import Decimal

from app.core.limiter import limiter
from app.core.security import create_access_token
from app.models.catalog import Category
from app.models.enums import EventType
from app.models.telemetry import UserEvent
from app.repositories import telemetry_repository, user_repository as repo
from app.services import order_service
from tests.test_checkout import GUEST, _form, _setup

GUEST_HEADERS = {"X-Cart-Session": "events-test-guest-token-0001", "X-Tracking-Consent": "granted"}


def _category(db):
    category = Category(slug="events-test-category")
    db.add(category)
    db.flush()
    return category


def _events(db, **filters):
    db.expire_all()
    return db.query(UserEvent).filter_by(**filters).all()


def test_guest_batch_is_stored(client, db_session):
    category = _category(db_session)
    body = {"events": [{"event_type": "CategoryView", "category_id": category.id, "metadata": {"page": 1}}]}
    assert client.post("/events", headers=GUEST_HEADERS, json=body).status_code == 204
    [event] = _events(db_session, session_token=GUEST_HEADERS["X-Cart-Session"])
    assert event.category_id == category.id and event.user_id is None


def test_without_consent_403(client):
    body = {"events": [{"event_type": "CategoryView"}]}
    headers = {"X-Cart-Session": GUEST_HEADERS["X-Cart-Session"]}
    assert client.post("/events", headers=headers, json=body).status_code == 403


def test_logged_in_header_cannot_override_profile(client, db_session):
    user = repo.create_user(db_session, "events.test@example.com", "not-a-real-hash")
    repo.create_user_profile(db_session, user.id, None, None)  # consent_analytics = false
    db_session.flush()
    headers = {"Authorization": f"Bearer {create_access_token(user.id, 'User')}", "X-Tracking-Consent": "granted"}
    assert client.post("/events", headers=headers, json={"events": [{"event_type": "CategoryView"}]}).status_code == 403


def test_validation_rejects_bad_batches(client):
    def post(body):
        return client.post("/events", headers=GUEST_HEADERS, json=body).status_code

    assert post({"events": []}) == 422
    assert post({"events": [{"event_type": "CategoryView"}] * 51}) == 422
    assert post({"events": [{"event_type": "Purchase"}]}) == 422
    assert post({"events": [{"event_type": "Hack"}]}) == 422
    assert post({"events": [{"event_type": "CategoryView", "user_id": 1}]}) == 422
    assert post({"events": [{"event_type": "CategoryView", "metadata": {"x": "a" * 2000}}]}) == 422
    assert post({"events": [{"event_type": "CategoryView", "metadata": {"x": {"nested": 1}}}]}) == 422


def test_unknown_product_dropped_without_500(client, db_session):
    body = {"events": [{"event_type": "ProductView", "product_id": 999_999_999}]}
    assert client.post("/events", headers=GUEST_HEADERS, json=body).status_code == 204
    assert _events(db_session, session_token=GUEST_HEADERS["X-Cart-Session"]) == []


def test_rate_limit_429(client):
    limiter.reset()
    body = {"events": [{"event_type": "CategoryView"}]}
    codes = [client.post("/events", headers=GUEST_HEADERS, json=body).status_code for _ in range(31)]
    assert codes[-1] == 429
    limiter.reset()


def test_purchase_recorded_only_with_consent(db_session):
    variant, method, _ = _setup(db_session, stock=3, quantity=2)
    order_service.checkout(db_session, _form(method.id), user_id=None, session_token=GUEST,
                           locale="uk", track_purchase=True)
    [event] = _events(db_session, event_type=EventType.Purchase, session_token=GUEST)
    assert event.variant_id == variant.id and event.event_metadata == {"quantity": 2}



def test_purchase_not_recorded_without_consent(db_session):
    _, method, _ = _setup(db_session)
    order_service.checkout(db_session, _form(method.id), user_id=None, session_token=GUEST, locale="uk")
    assert _events(db_session, event_type=EventType.Purchase, session_token=GUEST) == []



def test_link_guest_events(db_session):
    user = repo.create_user(db_session, "link.test@example.com", "not-a-real-hash")
    db_session.add(UserEvent(session_token="link-token-0000000001", event_type=EventType.CategoryView))
    db_session.flush()
    telemetry_repository.link_guest_events(db_session, "link-token-0000000001", user.id)
    assert len(_events(db_session, user_id=user.id)) == 1
