from datetime import datetime, timedelta, timezone
import secrets
import hashlib
import jwt 
import hmac
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.core.config import settings

_hasher = PasswordHasher()

def _pepper(password : str):
    return hmac.new(settings.password_pepper.encode(),password.encode(), hashlib.sha256).hexdigest()

def _verify(secret : str, hashed_password: str) -> bool:
    try: 
        return _hasher.verify(hashed_password,secret)
    except VerifyMismatchError:
        return False

def hash_password(password: str) -> str:
    return _hasher.hash(_pepper(password))

def verify_password(password: str, hashed_password: str) -> bool:
    return _verify(_pepper(password), hashed_password)

def verify_legacy_password(password: str,hashed_password: str)-> bool:
    return _verify(password,hashed_password)

def create_access_token(user_id: int, role: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "role": role,
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])

def generate_refresh_token() -> str:
    return secrets.token_urlsafe(settings.refresh_token_length)

def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

DUMMY_PASSWORD_HASH = hash_password(secrets.token_urlsafe(16))
