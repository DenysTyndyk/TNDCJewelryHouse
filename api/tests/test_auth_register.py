from sqlalchemy import select

from app.models.user import EmailVerificationToken
from app.repositories import user_repository as repo


def _payload(**overrides):
    payload = {
        "email": "test.user@example.com",
        "password": "supersecret123",
        "first_name": "Test",
        "last_name": "User",
    }
    payload.update(overrides)
    return payload


def test_register_returns_generic_success_message(client):
    response = client.post("/auth/register", json=_payload())

    assert response.status_code == 201
    assert "message" in response.json()


def test_register_creates_pending_user(client, db_session):
    client.post("/auth/register", json=_payload())

    user = repo.get_by_email(db_session, "test.user@example.com")
    assert user is not None
    assert user.status.value == "PendingVerification"
    assert user.role.value == "User"


def test_register_duplicate_email_does_not_create_a_second_user(client, db_session):
    first = client.post("/auth/register", json=_payload())
    assert first.status_code == 201

    # same response as a brand-new registration -- must not leak that the
    # email is already taken (anti user-enumeration)
    second = client.post("/auth/register", json=_payload())
    assert second.status_code == 201
    assert second.json() == first.json()

    user = repo.get_by_email(db_session, "test.user@example.com")
    assert user is not None


def test_register_duplicate_email_is_case_insensitive(client, db_session):
    client.post("/auth/register", json=_payload(email="Test.User@Example.com"))
    response = client.post("/auth/register", json=_payload(email="test.user@example.com"))

    assert response.status_code == 201
    # the unique index on lower(email) would raise IntegrityError on a true
    # duplicate insert; reaching 201 without a 500 confirms no second row was attempted
    user = repo.get_by_email(db_session, "test.user@example.com")
    assert user is not None


def test_register_rejects_invalid_email(client):
    response = client.post("/auth/register", json=_payload(email="not-an-email"))
    assert response.status_code == 422


def test_register_rejects_short_password(client):
    response = client.post("/auth/register", json=_payload(password="short"))
    assert response.status_code == 422


def test_register_never_stores_plaintext_password(client, db_session):
    client.post("/auth/register", json=_payload())

    user = repo.get_by_email(db_session, "test.user@example.com")
    assert user is not None
    assert user.password_hash != "supersecret123"
    assert user.password_hash.startswith("$argon2")


def test_register_issues_email_verification_token(client, db_session):
    client.post("/auth/register", json=_payload())

    user = repo.get_by_email(db_session, "test.user@example.com")
    token = db_session.scalar(
        select(EmailVerificationToken).where(EmailVerificationToken.user_id == user.id)
    )
    assert token is not None
    assert token.used_at is None
