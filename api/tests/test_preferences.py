from app.core.security import create_access_token
from app.repositories import user_repository as repo


def _headers(db_session, with_profile=True):
    user = repo.create_user(db_session, "lang.test@example.com", "not-a-real-hash")
    if with_profile:
        repo.create_user_profile(db_session, user.id, "Lang", "Test")
    db_session.flush()
    return {"Authorization": f"Bearer {create_access_token(user.id, "User")}"}


def test_me_returns_default_language(client, db_session):
    response = client.get("/auth/me", headers=_headers(db_session))
    assert response.status_code == 200
    assert response.json()["preferred_language"] == "uk"


def test_patch_preferences_persists_language(client, db_session):
    h = _headers(db_session)
    response = client.patch("/auth/me/preferences", headers=h, json={"preferred_language": "pl"})
    assert response.status_code == 200
    assert response.json()["preferred_language"] == "pl"
    assert client.get("/auth/me", headers=h).json()["preferred_language"] == "pl"


def test_patch_preferences_creates_missing_profile(client, db_session):
    h = _headers(db_session, with_profile=False)
    response = client.patch("/auth/me/preferences", headers=h, json={"preferred_language": "en"})
    assert response.json()["preferred_language"] == "en"


def test_patch_preferences_rejects_unknown_language(client, db_session):
    response = client.patch("/auth/me/preferences", headers=_headers(db_session), json={"preferred_language": "de"})
    assert response.status_code == 422


def test_patch_preferences_requires_token(client):
    assert client.patch("/auth/me/preferences", json={"preferred_language": "pl"}).status_code == 401
