from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.core.security import hash_refresh_token
from app.core.limiter import limiter
from app.repositories import user_repository as repo


def _register(client, email="negative.test@example.com", password="supersecret123"):
    response = client.post(
        "/auth/register",
        json={"email": email, "password": password, "first_name": "Neg", "last_name": "Test"},
    )
    assert response.status_code == 201
    return email, password


def _login(client, email, password):
    return client.post("/auth/login", json={"email": email, "password": password})


# —— Lockout ——


def test_account_locks_after_max_failed_attempts(client):
    email, password = _register(client)

    for _ in range(settings.max_failed_attempts):
        response = _login(client, email, "wrong-password")
        assert response.status_code == 401

    limiter.reset()  # isolate lockout behaviour from the HTTP rate limit, tested separately

    locked_response = _login(client, email, password)  # correct password, account still locked
    assert locked_response.status_code == 401
    assert "locked" in locked_response.json()["detail"].lower()


def test_successful_login_resets_failed_attempts(client, db_session):
    email, password = _register(client)

    _login(client, email, "wrong-password")
    _login(client, email, "wrong-password")
    assert _login(client, email, password).status_code == 200

    user = repo.get_by_email(db_session, email)
    assert user.failed_login_attempts == 0
    assert user.locked_until is None


# —— Refresh token reuse / expiry ——


def test_refresh_with_revoked_token_is_rejected(client):
    email, password = _register(client)
    login_response = _login(client, email, password)
    assert login_response.status_code == 200
    raw_token = login_response.cookies.get("refresh_token")

    logout_response = client.post("/auth/logout", cookies={"refresh_token": raw_token})
    assert logout_response.status_code == 204

    # simulate an attacker replaying a token captured before logout: the cookie
    # itself is marked Secure and gone from the browser/client jar by now, but
    # the revoked row must still be rejected if the raw value is replayed
    refresh_response = client.post("/auth/refresh", cookies={"refresh_token": raw_token})
    assert refresh_response.status_code == 401


def test_refresh_with_expired_token_is_rejected(client, db_session):
    email, password = _register(client)
    login_response = _login(client, email, password)
    raw_token = login_response.cookies.get("refresh_token")

    token = repo.get_refresh_token(db_session, hash_refresh_token(raw_token))
    token.expires_at = datetime.now(timezone.utc) - timedelta(days=1)
    db_session.flush()

    refresh_response = client.post("/auth/refresh", cookies={"refresh_token": raw_token})
    assert refresh_response.status_code == 401
    assert "expired" in refresh_response.json()["detail"].lower()


def test_refresh_without_cookie_is_rejected(client):
    response = client.post("/auth/refresh")
    assert response.status_code == 401


# —— SQL injection payloads ——


def test_login_sqli_in_email_is_rejected_by_validation(client):
    response = client.post(
        "/auth/login",
        json={"email": "' OR '1'='1' --", "password": "whatever"},
    )
    # malformed email never reaches the database query: pydantic rejects it first
    assert response.status_code == 422


def test_login_sqli_in_password_does_not_bypass_auth(client):
    email, _ = _register(client)

    response = _login(client, email, "' OR '1'='1")
    assert response.status_code == 401


def test_register_sqli_payload_does_not_break_request(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "sqli.test@example.com",
            "password": "supersecret123",
            "first_name": "Robert'); DROP TABLE users;--",
            "last_name": "Test",
        },
    )
    # first_name has no format restriction, so it is accepted and stored as a literal
    # string via a parameterized query -- it must never reach the DB as raw SQL.
    assert response.status_code == 201
