from app.core.security import create_access_token
from app.models.enums import EventType
from app.models.telemetry import UserEvent
from app.repositories import user_repository as repo
from app.services.telemetry_service import tracking_allowed


def _user(db_session, with_profile=True):
    user = repo.create_user(db_session, "consent.test@example.com", "not-a-real-hash")
    if with_profile:
        repo.create_user_profile(db_session, user.id, "Consent", "Test")
    db_session.flush()
    return user, {"Authorization": f"Bearer {create_access_token(user.id, 'User')}"}


def test_consent_defaults_to_false(client, db_session):
    _, h = _user(db_session)
    assert client.get("/auth/me", headers=h).json()["consent_analytics"] is False


def test_grant_consent_persists_and_sets_timestamp(client, db_session):
    user, h = _user(db_session)
    r = client.patch("/auth/me/consents", headers=h, json={"analytics": True})
    assert r.status_code == 200 and r.json()["consent_analytics"] is True
    assert repo.get_profile(db_session, user.id).consent_updated_at is not None


def test_repeated_same_value_keeps_timestamp(client, db_session):
    user, h = _user(db_session)
    client.patch("/auth/me/consents", headers=h, json={"analytics": True})
    first = repo.get_profile(db_session, user.id).consent_updated_at
    client.patch("/auth/me/consents", headers=h, json={"analytics": True})
    db_session.expire_all()
    assert repo.get_profile(db_session, user.id).consent_updated_at == first


def test_withdrawal_anonymises_events(client, db_session):
    user, h = _user(db_session)
    client.patch("/auth/me/consents", headers=h, json={"analytics": True})
    db_session.add(UserEvent(user_id=user.id, session_token="s" * 32, event_type=EventType.CategoryView))
    db_session.flush()

    client.patch("/auth/me/consents", headers=h, json={"analytics": False})

    db_session.expire_all()
    assert db_session.query(UserEvent).filter_by(user_id=user.id).count() == 0
    assert db_session.query(UserEvent).filter_by(session_token="s" * 32).count() == 0


def test_consent_creates_missing_profile(client, db_session):
    _, h = _user(db_session, with_profile=False)
    assert client.patch("/auth/me/consents", headers=h, json={"analytics": True}).json()["consent_analytics"] is True


def test_consent_requires_token_and_bool(client, db_session):
    assert client.patch("/auth/me/consents", json={"analytics": True}).status_code == 401
    _, h = _user(db_session)
    assert client.patch("/auth/me/consents", headers=h, json={"analytics": "yes"}).status_code == 422


def test_tracking_allowed_rule(db_session):
    user, _ = _user(db_session)
    assert tracking_allowed(db_session, None, "granted") is True
    assert tracking_allowed(db_session, None, None) is False
    assert tracking_allowed(db_session, None, "true") is False
    # Logged-in user without consent: header must not override the profile
    assert tracking_allowed(db_session, user.id, "granted") is False
    repo.get_profile(db_session, user.id).consent_analytics = True
    assert tracking_allowed(db_session, user.id, None) is True
