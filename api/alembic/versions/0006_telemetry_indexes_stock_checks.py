"""Telemetry indexes (created_at, search_queries lookups) and stock/sale CHECK constraints

Revision ID: 0006
Revises: 0005
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index("ix_user_events_created_at", "user_events", ["created_at"])
    op.create_index("ix_search_queries_session_token", "search_queries", ["session_token"])
    op.create_index("ix_search_queries_user_id", "search_queries", ["user_id"])
    op.create_check_constraint(
        op.f("ck_product_variants_reserved_le_stock"),
        "product_variants",
        "reserved_quantity <= stock_quantity",
    )
    op.create_check_constraint(
        op.f("ck_variant_prices_sale_below_price"),
        "variant_prices",
        "sale_price IS NULL OR sale_price < price",
    )


def downgrade() -> None:
    op.drop_constraint(op.f("ck_variant_prices_sale_below_price"), "variant_prices", type_="check")
    op.drop_constraint(op.f("ck_product_variants_reserved_le_stock"), "product_variants", type_="check")
    op.drop_index("ix_search_queries_user_id", table_name="search_queries")
    op.drop_index("ix_search_queries_session_token", table_name="search_queries")
    op.drop_index("ix_user_events_created_at", table_name="user_events")
