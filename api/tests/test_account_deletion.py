from datetime import datetime, timedelta, timezone

from app.core.security import create_access_token, hash_password
from app.models.commerce import Order
from app.models.enums import EventType
from app.models.telemetry import UserEvent
from app.repositories import telemetry_repository, user_repository as repo
from app.services import order_service
from tests.test_checkout import GUEST, _form, _setup

PASSWORD = "Correct-Horse-42"
TOKEN = "delete-test-session-0000001"


def _user(db):
    user = repo.create_user(db, "delete.test@example.com", hash_password(PASSWORD))
    repo.create_user_profile(db, user.id, "Del", "Ete")
    db.flush()
    return user, {"Authorization": f"Bearer {create_access_token(user.id, 'User')}"}


def _delete(client, headers, password):
    # TestClient.delete() has no json= argument, hence request()
    return client.request("DELETE", "/auth/me", headers=headers, json={"password": password})


def test_wrong_password_keeps_account(client, db_session):
    user, h = _user(db_session)
    assert _delete(client, h, "wrong").status_code == 403
    assert repo.get_by_id(db_session, user.id) is not None


def test_delete_removes_user_anonymises_events_keeps_orders(client, db_session):
    user, h = _user(db_session)
    db_session.add(UserEvent(user_id=user.id, session_token=TOKEN, event_type=EventType.CategoryView))
    _, method, _ = _setup(db_session)
    out = order_service.checkout(db_session, _form(method.id), user_id=None, session_token=GUEST, locale="uk")
    order = db_session.query(Order).filter_by(order_number=out.order_number).one()
    order.user_id = user.id
    db_session.flush()

    assert _delete(client, h, PASSWORD).status_code == 204

    db_session.expire_all()
    assert repo.get_by_id(db_session, user.id) is None
    assert repo.get_profile(db_session, user.id) is None
    assert db_session.query(UserEvent).filter_by(session_token=TOKEN).count() == 0
    assert db_session.query(UserEvent).filter_by(user_id=user.id).count() == 0
    kept = db_session.get(Order, order.id)
    assert kept is not None and kept.user_id is None


def test_token_rejected_after_deletion(client, db_session):
    _, h = _user(db_session)
    _delete(client, h, PASSWORD)
    assert client.get("/auth/me", headers=h).status_code == 401


def test_retention_anonymises_only_old_events(db_session):
    now = datetime.now(timezone.utc)
    old = UserEvent(session_token="old-" + TOKEN, event_type=EventType.CategoryView,
                    created_at=now - timedelta(days=400))
    fresh = UserEvent(session_token="new-" + TOKEN, event_type=EventType.CategoryView)
    db_session.add_all([old, fresh])
    db_session.flush()

    counts = telemetry_repository.anonymize_older_than(db_session, now - timedelta(days=365))
    db_session.expire_all()

    assert counts["user_events"] == 1
    assert old.session_token is None
    assert fresh.session_token == "new-" + TOKEN
    # Re-run is a no-op
    assert telemetry_repository.anonymize_older_than(db_session, now - timedelta(days=365))["user_events"] == 0
