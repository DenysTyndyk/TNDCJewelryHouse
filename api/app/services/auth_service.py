from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
import logging
from app.models.enums import UserStatus
from app.models.user import User
from app.core.config import settings
from app.core.security import (
    DUMMY_PASSWORD_HASH,
    create_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.repositories import user_repository as repo

class AuthError(Exception):
    pass

def register(db: Session, email: str, password: str, first_name: str | None, last_name: str | None) -> None:
   if repo.get_by_email(db, email):
        return
   user = repo.create_user(db, email, password_hash=hash_password(password))
   repo.create_user_profile(db, user.id, first_name, last_name)
   _issue_email_verification_token(db,user)
   db.commit()

def login(db: Session, email: str, password: str) -> tuple[str, str,int]:
   user = repo.get_by_email(db,email)
   if not user:
    verify_password(password, DUMMY_PASSWORD_HASH)  
    raise AuthError("Invalid email or password")
   if user.status in (UserStatus.Suspended, UserStatus.Deactivated):
    raise AuthError("Account is not available")
   if repo.is_locked(user):
    raise AuthError("Account is locked due to too many failed login attempts. Please try again later.")
   if not verify_password(password, user.password_hash):
    repo.register_failed_login(db, user)
    db.commit()
    raise AuthError("Invalid email or password")
   repo.register_successful_login(db, user)
   access_token = create_access_token(user.id,user.role.value)
   refresh_token = _issue_refresh_token(db, user.id)
   db.commit()
   return access_token, refresh_token, user.id

def refresh(db: Session, raw_refresh_token: str) -> tuple[str, str]:
    token_hash = hash_refresh_token(raw_refresh_token)
    token = repo.get_refresh_token(db, token_hash)
    if token is None:
        raise AuthError("Invalid refresh token")
    if token.revoked_at is not None:
        grace = timedelta(seconds=settings.refresh_reuse_grace_seconds)
        if datetime.now(timezone.utc) - token.revoked_at > grace:
            repo.revoke_all_for_user(db, token.user_id)
            db.commit()
            raise AuthError("refresh token reuse detected")
        
        raise AuthError("Invalid refresh token")
    if token.expires_at < datetime.now(timezone.utc):
        raise AuthError("Refresh token has expired")

    repo.revoke_refresh_token(db, token)
    user = repo.get_by_id(db, token.user_id)
    if user is None:
        raise AuthError("Invalid refresh token")
    access_token = create_access_token(user.id, user.role.value)
    new_refresh_token = _issue_refresh_token(db, user.id)
    db.commit()
    return access_token, new_refresh_token

def logout(db: Session, raw_refresh_token: str) -> None:
    token_hash = hash_refresh_token(raw_refresh_token)
    token = repo.get_refresh_token(db,token_hash)
    if token is not None:
       repo.revoke_refresh_token(db, token)
       db.commit()

def verify_email(db: Session, raw_token: str) -> None:
    token_hash = hash_refresh_token(raw_token)
    token = repo.get_email_verification_token(db, token_hash)
    if token is None or token.used_at is not None:
        raise AuthError("Invalid or already used verification token")
    if token.expires_at < datetime.now(timezone.utc):
        raise AuthError("Verification token has expired")
    repo.mark_email_verification_used(db, token)
    user = repo.get_by_id(db, token.user_id)
    user.status = UserStatus.Active
    user.email_verified_at = datetime.now(timezone.utc)
    db.commit()

def forgot_password(db: Session, email: str) -> None:
   user = repo.get_by_email(db,email)
   if user is not None:
      _issue_password_reset_token(db,user)
      db.commit()

def reset_password(db: Session, raw_token: str, new_password: str) -> None:
    token_hash = hash_refresh_token(raw_token)
    token = repo.get_password_reset_token(db, token_hash)
    if token is None or token.used_at is not None:
       raise AuthError("Invalid or already used reset token")
    if token.expires_at < datetime.now(timezone.utc):
       raise AuthError("Reset token has expired")
    repo.mark_password_reset_used(db, token)
    user = repo.get_by_id(db, token.user_id)
    if user is None:
        raise AuthError("Invalid or already used reset token")
    repo.update_password(db, user, hash_password(new_password))
    repo.revoke_all_for_user(db, user.id)
    db.commit()

def _issue_refresh_token(db: Session, user_id: int) -> str:
   raw_token = generate_refresh_token()
   expires_at = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
   repo.store_refresh_token(db, user_id, hash_refresh_token(raw_token), expires_at)
   return raw_token

def _issue_email_verification_token(db: Session, user:User) ->  None:
    raw_token = generate_refresh_token()
    expires_at = datetime.now(timezone.utc) + timedelta(hours = settings.email_verification_token_expire_hours)
    repo.create_email_verification_token(db,user.id,hash_refresh_token(raw_token), expires_at)
    link = f"{settings.frontend_base_url}/verify-email?token={raw_token}"
    logging.getLogger("app").info("EMAIL_VERIFICATION_LINK user_id=%s link=%s", user.id, link)

def _issue_password_reset_token(db: Session, user: User) -> None:
    repo.invalidate_active_password_reset_tokens(db, user.id)
    raw_token = generate_refresh_token()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.password_reset_token_expire_minutes)
    repo.create_password_reset_token(db, user.id, hash_refresh_token(raw_token), expires_at)
    link = f"{settings.frontend_base_url}/reset-password?token={raw_token}"
    logging.getLogger("app").info("PASSWORD_RESET_LINK user_id=%s link=%s", user.id, link)