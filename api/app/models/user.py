from datetime import date, datetime
from typing import Optional

from sqlalchemy import ForeignKey, Index, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, bigint_pk, created_at_col, updated_at_col
from app.models.enums import Role, UserStatus, pg_enum


class User(Base):
    __tablename__ = "users"

    id: Mapped[bigint_pk]
    email: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(pg_enum(Role, "user_role"), server_default="User")
    status: Mapped[UserStatus] = mapped_column(
        pg_enum(UserStatus, "user_status"), server_default="PendingVerification"
    )
    password_hash: Mapped[str] = mapped_column(String(255))  # argon2id, never plaintext
    failed_login_attempts: Mapped[int] = mapped_column(server_default=text("0"))
    locked_until: Mapped[Optional[datetime]]
    email_verified_at: Mapped[Optional[datetime]]
    last_login_at: Mapped[Optional[datetime]]
    created_at: Mapped[created_at_col]
    updated_at: Mapped[updated_at_col]
    deleted_at: Mapped[Optional[datetime]]

    __table_args__ = (
        # Partial + case-insensitive: a soft-deleted user can register again.
        Index(
            "ix_users_email_active",
            text("lower(email)"),
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[bigint_pk]
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )
    first_name: Mapped[Optional[str]] = mapped_column(String(100))
    last_name: Mapped[Optional[str]] = mapped_column(String(100))
    phone_number: Mapped[Optional[str]] = mapped_column(String(32))
    date_of_birth: Mapped[Optional[date]]
    preferred_language: Mapped[str] = mapped_column(String(10), server_default="uk")
    consent_personal_data: Mapped[bool] = mapped_column(server_default=text("false"))
    consent_marketing: Mapped[bool] = mapped_column(server_default=text("false"))
    consent_updated_at: Mapped[Optional[datetime]]
    created_at: Mapped[created_at_col]
    updated_at: Mapped[updated_at_col]

    __table_args__ = (
        Index(
            "ix_user_profiles_phone_number",
            "phone_number",
            unique=True,
            postgresql_where=text("phone_number IS NOT NULL"),
        ),
    )


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[bigint_pk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    token_hash: Mapped[str] = mapped_column(String(255), unique=True)
    device_info: Mapped[Optional[str]] = mapped_column(String(255))
    ip_address: Mapped[Optional[str]] = mapped_column(String(64))
    expires_at: Mapped[datetime]
    revoked_at: Mapped[Optional[datetime]]
    created_at: Mapped[created_at_col]

    __table_args__ = (Index("ix_refresh_tokens_user_id", "user_id"),)


class EmailVerificationToken(Base):
    __tablename__ = "email_verification_tokens"

    id: Mapped[bigint_pk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    token_hash: Mapped[str] = mapped_column(String(255), unique=True)
    expires_at: Mapped[datetime]
    used_at: Mapped[Optional[datetime]]
    created_at: Mapped[created_at_col]

    __table_args__ = (Index("ix_email_verification_tokens_user_id", "user_id"),)


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id: Mapped[bigint_pk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    token_hash: Mapped[str] = mapped_column(String(255), unique=True)
    expires_at: Mapped[datetime]
    used_at: Mapped[Optional[datetime]]
    created_at: Mapped[created_at_col]

    __table_args__ = (Index("ix_password_reset_tokens_user_id", "user_id"),)
