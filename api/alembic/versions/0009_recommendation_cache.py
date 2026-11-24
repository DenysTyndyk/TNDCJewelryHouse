from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0009"
down_revision: Union[str, None] = "0008"

def upgrade() -> None:
    op.create_table(
        "recommendation_cache",
        sa.Column("cache_key", sa.String(200), primary_key=True),
        sa.Column("owner_key", sa.String(140), nullable=False),
        sa.Column("algorithm", sa.String(20), nullable=False),
        sa.Column("product_ids", postgresql.ARRAY(sa.BigInteger()), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_recommendation_cache_owner_key", "recommendation_cache", ["owner_key"])
    op.create_index("ix_recommendation_cache_expires_at", "recommendation_cache", ["expires_at"])

def downgrade() -> None:
    op.drop_table("recommendation_cache")