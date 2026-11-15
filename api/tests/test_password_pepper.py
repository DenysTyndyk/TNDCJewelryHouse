from argon2 import PasswordHasher

from app.core import security
from app.core.security import hash_password, verify_legacy_password, verify_password
from app.repositories import user_repository as repo


def test_hash_is_peppered():
    hashed = hash_password("supersecret123")
    assert verify_password("supersecret123", hashed)
    assert not verify_legacy_password("supersecret123", hashed)


def test_wrong_pepper_is_rejected(monkeypatch):
    hashed = hash_password("supersecret123")
    monkeypatch.setattr(security.settings, "password_pepper", "x" * 32)
    assert not verify_password("supersecret123", hashed)


def test_legacy_hash_is_upgraded_on_login(client, db_session):
    email, password = "legacy.pepper@example.com", "supersecret123"
    response = client.post("/auth/register", json={"email": email, "password": password, "first_name": "Legacy", "last_name": "User"})
    assert response.status_code == 201
    user = repo.get_by_email(db_session, email)
    user.password_hash = PasswordHasher().hash(password) 
    db_session.commit()

    assert client.post("/auth/login", json={"email": email, "password": password}).status_code == 200

    db_session.refresh(user)
    assert verify_password(password, user.password_hash)
