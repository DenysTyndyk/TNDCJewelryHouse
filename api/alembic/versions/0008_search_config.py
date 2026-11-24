"""Text search config tndc_search: simple + unaccent for uk/pl/en

Revision ID: 0008
Revises: 0007
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0008"
down_revision: Union[str, None] = "0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS unaccent")
    op.execute("CREATE TEXT SEARCH CONFIGURATION tndc_search (COPY = simple)")
    op.execute(
        "ALTER TEXT SEARCH CONFIGURATION tndc_search "
        "ALTER MAPPING FOR hword, hword_part, word WITH unaccent, simple"
    )

def downgrade() -> None:
    op.execute("DROP TEXT SEARCH CONFIGURATION IF EXISTS tndc_search")
