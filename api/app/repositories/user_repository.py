from datetime import datetime, timedelta, timezone

from sqlalchemy import select,func
from sqlalchemy.orm import Session

from app.models.user import User, RefreshToken,UserProfile,EmailVerificationToken, PasswordResetToken
from app.core.config import settings

def get_by_email(db: Session, email: str) -> User | None:
    stmt = select(User).where(func.lower(User.email) == email.lower(), User.deleted_at.is_(None))
    return db.scalar(stmt)

def get_by_id(db: Session, user_id: int) -> User | None:
    stmt = select(User).where(User.id == user_id, User.deleted_at.is_(None))
    return db.scalar(stmt)

def create_user(db: Session, email: str, password_hash: str) -> User:
    user = User(email=email, password_hash=password_hash)
    db.add(user)
    db.flush()
    return user

def register_failed_login(db: Session, user: User) -> None:
    if user.locked_until is not None and user.locked_until <= datetime.now(timezone.utc):
        user.failed_login_attempts = 0
    user.failed_login_attempts += 1
    if user.failed_login_attempts >= settings.max_failed_attempts:
        user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=settings.lockout_duration)
    db.flush()

def register_successful_login(db: Session, user: User) -> None:
    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login_at = datetime.now(timezone.utc)
    db.flush()

def is_locked(user: User) -> bool:
    return user.locked_until is not None and user.locked_until > datetime.now(timezone.utc)

def store_refresh_token(db: Session, user_id: int, token_hash: str, expires_at: datetime) -> RefreshToken | None:
    token = RefreshToken(user_id=user_id, token_hash=token_hash, expires_at=expires_at)
    db.add(token)
    db.flush()
    return token

def get_refresh_token(db: Session, token_hash: str) -> RefreshToken | None:
    stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    return db.scalar(stmt)

def revoke_refresh_token(db : Session, token: RefreshToken) -> None:
    token.revoked_at = datetime.now(timezone.utc)
    db.flush()

def revoke_all_for_user(db: Session, user_id: int) -> None:
    stmt = select(RefreshToken).where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
    for token in db.scalars(stmt):
        token.revoked_at = datetime.now(timezone.utc)
    db.flush()

def create_user_profile(db: Session, user_id: int, first_name: str | None, last_name: str | None, phone_number: str | None = None) -> UserProfile:
    profile = UserProfile(user_id=user_id, first_name=first_name, last_name=last_name, phone_number=phone_number)
    db.add(profile)
    db.flush()
    return profile

def get_profile(db: Session, user_id: int) -> UserProfile | None:
    return db.scalar(select(UserProfile).where(UserProfile.user_id == user_id))

def get_by_phone_number(db: Session, phone_number: str) -> UserProfile | None:
    stmt = select(UserProfile).where(UserProfile.phone_number == phone_number)
    return db.scalar(stmt)

def create_email_verification_token(db: Session, user_id: int, token_hash: str, expires_at: datetime) -> EmailVerificationToken:
    token = EmailVerificationToken(user_id=user_id, token_hash=token_hash, expires_at=expires_at)
    db.add(token)
    db.flush()
    return token

def get_email_verification_token(db: Session, token_hash: str) -> EmailVerificationToken | None:
    stmt = select(EmailVerificationToken).where(EmailVerificationToken.token_hash == token_hash)
    return db.scalar(stmt)

def mark_email_verification_used(db: Session, token: EmailVerificationToken) -> None:
    token.used_at = datetime.now(timezone.utc)
    db.flush()

def create_password_reset_token(db: Session, user_id: int, token_hash: str, expires_at: datetime) -> PasswordResetToken:
    token = PasswordResetToken(user_id=user_id, token_hash=token_hash, expires_at=expires_at)
    db.add(token)
    db.flush()
    return token

def get_password_reset_token(db: Session, token_hash: str)-> PasswordResetToken | None:
    stmt = select(PasswordResetToken).where(PasswordResetToken.token_hash == token_hash)
    return db.scalar(stmt)

def mark_password_reset_used(db: Session, token: PasswordResetToken) -> None:
    token.used_at = datetime.now(timezone.utc)
    db.flush()

def invalidate_active_password_reset_tokens(db: Session, user_id: int) -> None:
    stmt = select(PasswordResetToken).where(
        PasswordResetToken.user_id == user_id,
        PasswordResetToken.used_at.is_(None),
    )
    now = datetime.now(timezone.utc)
    for token in db.scalars(stmt):
        token.used_at = now
    db.flush()

def update_password(db:Session, user: User, password_hash: str) -> None:
    user.password_hash = password_hash
    db.flush()