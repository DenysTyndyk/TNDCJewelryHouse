"""T0.3: every seeded price has a price_history entry (Omnibus source)."""
import pytest
from sqlalchemy import exists, func, select

from app.models import PriceHistory, VariantPrice


def test_every_variant_price_has_history(db_session):
    # Runs against the seeded dev DB; other tests roll back, so only seed/admin/import data is visible here
    if db_session.scalar(select(func.count()).select_from(VariantPrice)) == 0:
        pytest.skip("DB is not seeded: run python -m scripts.seed first")

    has_history = exists().where(
        PriceHistory.variant_id == VariantPrice.variant_id,
        PriceHistory.currency == VariantPrice.currency,
    )
    missing = db_session.scalars(select(VariantPrice.variant_id).where(~has_history)).all()
    assert missing == [], f"variants without price_history: {missing}"
