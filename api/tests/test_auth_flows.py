import re
from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.core.limiter import limiter
from app.core.security import hash_refresh_token
from app.repositories import user_repository as repo


def _register(client, email="flow.test@example.com", password="supersecret123"):
    response = client.post(
        "/auth/register",
        json={"email": email, "password": password, "first_name": "Flow", "last_name": "Test"},
    )
    assert response.status_code == 201
    return email, password


def _login(client, email, password):
    return client.post("/auth/login", json={"email": email, "password": password})


def _extract_token_from_log(caplog, marker):
    match = re.search(rf"{marker}.*?token=(\S+)", caplog.text)
    assert match, f"{marker} not found in logs"
    return match.group(1)


# —— /auth/me ——


def test_me_requires_bearer_token(client):
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_me_returns_current_user(client):
    email, password = _register(client)
    login_response = _login(client, email, password)
    access_token = login_response.json()["access_token"]

    response = client.get("/auth/me", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json()["email"] == email


def test_me_rejects_garbage_token(client):
    response = client.get("/auth/me", headers={"Authorization": "Bearer not-a-real-token"})
    assert response.status_code == 401


# —— /auth/verify-email ——


def test_verify_email_activates_pending_user(client, db_session, caplog):
    import logging

    caplog.set_level(logging.INFO, logger="app")
    email, _ = _register(client)
    raw_token = _extract_token_from_log(caplog, "EMAIL_VERIFICATION_LINK")

    response = client.get(f"/auth/verify-email?token={raw_token}")
    assert response.status_code == 200

    user = repo.get_by_email(db_session, email)
    assert user.status.value == "Active"
    assert user.email_verified_at is not None


def test_verify_email_rejects_unknown_token(client):
    response = client.get("/auth/verify-email?token=does-not-exist")
    assert response.status_code == 400


def test_verify_email_rejects_reused_token(client, caplog):
    import logging

    caplog.set_level(logging.INFO, logger="app")
    _register(client)
    raw_token = _extract_token_from_log(caplog, "EMAIL_VERIFICATION_LINK")

    first = client.get(f"/auth/verify-email?token={raw_token}")
    assert first.status_code == 200

    second = client.get(f"/auth/verify-email?token={raw_token}")
    assert second.status_code == 400


# —— /auth/forgot-password + /auth/reset-password ——


def test_forgot_password_for_unknown_email_is_still_generic_200(client):
    response = client.post("/auth/forgot-password", json={"email": "nobody@example.com"})
    assert response.status_code == 200


def test_reset_password_changes_password_and_revokes_sessions(client, caplog):
    import logging

    caplog.set_level(logging.INFO, logger="app")
    email, old_password = _register(client)

    login_response = _login(client, email, old_password)
    refresh_token = login_response.cookies.get("refresh_token")

    forgot_response = client.post("/auth/forgot-password", json={"email": email})
    assert forgot_response.status_code == 200
    raw_reset_token = _extract_token_from_log(caplog, "PASSWORD_RESET_LINK")

    new_password = "brandnewpassword123"
    reset_response = client.post(
        "/auth/reset-password", json={"token": raw_reset_token, "new_password": new_password}
    )
    assert reset_response.status_code == 200

    assert _login(client, email, old_password).status_code == 401
    assert _login(client, email, new_password).status_code == 200

    # the session that existed before the reset must be revoked
    stale_refresh = client.post("/auth/refresh", cookies={"refresh_token": refresh_token})
    assert stale_refresh.status_code == 401


def test_reset_password_rejects_unknown_token(client):
    response = client.post(
        "/auth/reset-password", json={"token": "does-not-exist", "new_password": "whatever123"}
    )
    assert response.status_code == 400


def test_reset_password_rejects_reused_token(client, caplog):
    import logging

    caplog.set_level(logging.INFO, logger="app")
    email, _ = _register(client)
    client.post("/auth/forgot-password", json={"email": email})
    raw_reset_token = _extract_token_from_log(caplog, "PASSWORD_RESET_LINK")

    first = client.post(
        "/auth/reset-password", json={"token": raw_reset_token, "new_password": "firstnewpass123"}
    )
    assert first.status_code == 200

    second = client.post(
        "/auth/reset-password", json={"token": raw_reset_token, "new_password": "secondnewpass123"}
    )
    assert second.status_code == 400


# —— /auth/refresh: success, rotation, reuse detection ——


def test_refresh_rotates_the_token_and_issues_a_new_access_token(client):
    email, password = _register(client)
    login_response = _login(client, email, password)
    old_refresh_token = login_response.cookies.get("refresh_token")

    refresh_response = client.post("/auth/refresh", cookies={"refresh_token": old_refresh_token})
    assert refresh_response.status_code == 200
    assert refresh_response.json()["access_token"]  

    new_refresh_token = refresh_response.cookies.get("refresh_token")
    assert new_refresh_token is not None
    assert new_refresh_token != old_refresh_token

    # the old (now rotated-out) token must no longer work
    replay_response = client.post("/auth/refresh", cookies={"refresh_token": old_refresh_token})
    assert replay_response.status_code == 401


def test_refresh_reuse_outside_grace_window_revokes_all_sessions(client, db_session):
    email, password = _register(client)
    login_response = _login(client, email, password)
    raw_token = login_response.cookies.get("refresh_token")

    # rotate once, then backdate the now-revoked old token past the grace window
    client.post("/auth/refresh", cookies={"refresh_token": raw_token})
    token = repo.get_refresh_token(db_session, hash_refresh_token(raw_token))
    token.revoked_at = datetime.now(timezone.utc) - timedelta(
        seconds=settings.refresh_reuse_grace_seconds + 1
    )
    db_session.flush()

    replay_response = client.post("/auth/refresh", cookies={"refresh_token": raw_token})
    assert replay_response.status_code == 401
    assert "reuse" in replay_response.json()["detail"].lower()

    user = repo.get_by_email(db_session, email)
    assert repo.get_refresh_token(db_session, hash_refresh_token(raw_token)).user_id == user.id
    # every refresh token for this user should now be revoked
    from sqlalchemy import select
    from app.models.user import RefreshToken

    tokens = db_session.scalars(select(RefreshToken).where(RefreshToken.user_id == user.id)).all()
    assert all(t.revoked_at is not None for t in tokens)


# —— Rate limit (429) ——


def test_login_is_rate_limited(client):
    limiter.reset()
    email, password = _register(client)

    for _ in range(5):
        response = _login(client, email, "wrong-password")
        assert response.status_code == 401

    response = _login(client, email, "wrong-password")
    assert response.status_code == 429
