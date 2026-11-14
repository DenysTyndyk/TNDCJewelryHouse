"""checkout constraints: one active cart per user, unique provider payment id, order number sequence

Revision ID: 0004
Revises: 0003
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Concurrent "add to cart" requests must not create two active carts for one user
    op.create_index(
        "uq_carts_user_active", "carts", ["user_id"], unique=True,
        postgresql_where=sa.text("status = 'Active'"),
    )
    # A repeated provider webhook must not create a second payment row (NULLs stay distinct: pending payments)
    op.create_index("uq_payments_provider_external_id", "payments", ["provider", "external_id"], unique=True)
    # Gap-tolerant, race-free counter for TNDC-YYYY-NNNNN order numbers
    op.execute("CREATE SEQUENCE order_number_seq")


def downgrade() -> None:
    op.execute("DROP SEQUENCE IF EXISTS order_number_seq")
    op.drop_index("uq_payments_provider_external_id", table_name="payments")
    op.drop_index("uq_carts_user_active", table_name="carts")
