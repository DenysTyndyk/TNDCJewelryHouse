"""Drop users.deleted_at: accounts are hard-deleted (RODO), soft delete is not used

Revision ID: 0007
Revises: 0006
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0007"
down_revision: Union[str, None] = "0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # The partial index references deleted_at, so it must go before the column.
    op.drop_index("ix_users_email_active", table_name="users", postgresql_where=sa.text("deleted_at IS NULL"))
    op.drop_column("users", "deleted_at")
    op.create_index("ix_users_email_active", "users", [sa.literal_column("lower(email)")], unique=True)


def downgrade() -> None:
    op.drop_index("ix_users_email_active", table_name="users")
    op.add_column("users", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index(
        "ix_users_email_active", "users", [sa.literal_column("lower(email)")],
        unique=True, postgresql_where=sa.text("deleted_at IS NULL"),
    )
