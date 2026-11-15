"""End-to-end telemetry flows over HTTP (M5 T7.4, T7.5) and the API fields the frontend relies on (T6)."""
from app.core.security import create_access_token, hash_password
from app.models.enums import EventType
from app.models.telemetry import UserEvent
from app.repositories import user_repository as repo
from tests.test_checkout import GUEST, _form, _setup

PASSWORD = "Tracking-Flow-42"
GUEST_TOKEN = "tracking-flow-guest-token-01"


def _user(db, email, consent: bool):
    user = repo.create_user(db, email, hash_password(PASSWORD))
    profile = repo.create_user_profile(db, user.id, "Track", "Flow")
    profile.consent_analytics = consent
    db.flush()
    return user


def _guest_event(db):
    db.add(UserEvent(session_token=GUEST_TOKEN, event_type=EventType.CategoryView))
    db.flush()


def _login(client, email):
    return client.post(
        "/auth/login",
        headers={"X-Cart-Session": GUEST_TOKEN},
        json={"email": email, "password": PASSWORD},
    )


def _events(db, **filters):
    db.expire_all()
    return db.query(UserEvent).filter_by(**filters).all()


# —— T7.5: login links guest events only with the account's own consent ——

def test_login_links_guest_events_when_account_consented(client, db_session):
    user = _user(db_session, "link.yes@example.com", consent=True)
    _guest_event(db_session)

    assert _login(client, "link.yes@example.com").status_code == 200

    [event] = _events(db_session, session_token=GUEST_TOKEN)
    assert event.user_id == user.id


def test_login_does_not_link_without_account_consent(client, db_session):
    _user(db_session, "link.no@example.com", consent=False)
    _guest_event(db_session)

    assert _login(client, "link.no@example.com").status_code == 200

    [event] = _events(db_session, session_token=GUEST_TOKEN)
    assert event.user_id is None


def test_login_never_steals_events_of_another_account(client, db_session):
    owner = _user(db_session, "link.owner@example.com", consent=True)
    _user(db_session, "link.other@example.com", consent=True)
    db_session.add(UserEvent(user_id=owner.id, session_token=GUEST_TOKEN, event_type=EventType.CategoryView))
    db_session.flush()

    _login(client, "link.other@example.com")

    [event] = _events(db_session, session_token=GUEST_TOKEN)
    assert event.user_id == owner.id


# —— T7.4 over HTTP: the router turns the consent header into track_purchase ——

def _checkout(client, method_id, consent_header: bool):
    headers = {"X-Cart-Session": GUEST}
    if consent_header:
        headers["X-Tracking-Consent"] = "granted"
    return client.post("/orders", headers=headers, json=_form(method_id).model_dump(mode="json"))


def test_guest_checkout_with_consent_records_purchase(client, db_session):
    variant, method, _ = _setup(db_session, stock=3, quantity=2)
    assert _checkout(client, method.id, consent_header=True).status_code == 201

    [event] = _events(db_session, event_type=EventType.Purchase, variant_id=variant.id)
    assert event.product_id == variant.product_id
    assert event.event_metadata == {"quantity": 2}  # no order number: it would undo anonymisation


def test_guest_checkout_without_consent_records_nothing(client, db_session):
    variant, method, _ = _setup(db_session)
    assert _checkout(client, method.id, consent_header=False).status_code == 201
    assert _events(db_session, event_type=EventType.Purchase, variant_id=variant.id) == []


# —— T6: fields the frontend depends on ——

def test_me_exposes_consent_decision_time(client, db_session):
    user = _user(db_session, "me.consent@example.com", consent=False)
    h = {"Authorization": f"Bearer {create_access_token(user.id, 'User')}"}

    assert client.get("/auth/me", headers=h).json()["consent_updated_at"] is None  # never decided → banner
    client.patch("/auth/me/consents", headers=h, json={"analytics": True})
    me = client.get("/auth/me", headers=h).json()
    assert me["consent_analytics"] is True and me["consent_updated_at"] is not None


def test_cart_line_has_product_id(client, db_session):
    variant, _, _ = _setup(db_session)
    [line] = client.get("/cart", headers={"X-Cart-Session": GUEST}).json()["items"]
    assert line["product_id"] == variant.product_id
