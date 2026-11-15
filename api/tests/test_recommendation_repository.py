from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.models.catalog import (
    Category, Gemstone, Product, ProductGemstone, ProductVariant, VariantPrice,
)
from app.models.enums import Currency, EventType, MetalColor, MetalType
from app.models.telemetry import UserEvent
from app.repositories import recommendation_repository as repo

NOW = datetime.now(timezone.utc)
GUEST = "reco-repo-test-guest-0001"
WEIGHTED = [EventType.ProductView, EventType.Search]


def _product(db, slug, *, published=True):
    category = Category(slug=f"{slug}-cat")
    db.add(category)
    db.flush()
    product = Product(
        category_id=category.id,
        slug=slug,
        published_at=NOW - timedelta(days=1) if published else None,
    )
    db.add(product)
    db.flush()
    return product


def _variant(db, product, sku, price, stock, **attrs):
    variant = ProductVariant(
        product_id=product.id, sku=sku, base_price=Decimal(price), stock_quantity=stock, **attrs
    )
    db.add(variant)
    db.flush()
    db.add(VariantPrice(variant_id=variant.id, currency=Currency.UAH, price=Decimal(price)))
    db.flush()


def _event(db, event_type, product_id, days_ago, token=GUEST):
    db.add(UserEvent(
        session_token=token,
        event_type=event_type,
        product_id=product_id,
        created_at=NOW - timedelta(days=days_ago),
    ))


def test_features_aggregate_variants_and_gemstones(db_session):
    product = _product(db_session, "reco-test-ring")
    _variant(db_session, product, "RECO-1", "1000.00", 0,
             metal_type=MetalType.Gold, metal_color=MetalColor.White, fineness=585)
    _variant(db_session, product, "RECO-2", "800.00", 2,
             metal_type=MetalType.Gold, fineness=750)
    gem = Gemstone(slug="reco-test-gem", name="Test gem")
    db_session.add(gem)
    db_session.flush()
    db_session.add(ProductGemstone(product_id=product.id, gemstone_id=gem.id))
    draft = _product(db_session, "reco-test-draft", published=False)
    _variant(db_session, draft, "RECO-3", "500.00", 1)
    db_session.flush()

    rows = {r.id: r for r in repo.load_product_features(db_session)}

    row = rows[product.id]
    assert row.metals == ["Gold"]             
    assert row.colors == ["White"]             
    assert sorted(row.finenesses) == [585, 750]
    assert row.gemstones == [gem.id]
    assert row.price == Decimal("800.00")      
    assert row.available is True               
    assert draft.id not in rows                


def test_history_keeps_only_recent_product_events(db_session):
    product = _product(db_session, "reco-test-hist")
    _event(db_session, EventType.ProductView, product.id, 1)
    _event(db_session, EventType.Search, None, 1)                
    _event(db_session, EventType.CategoryView, product.id, 1)    
    _event(db_session, EventType.ProductView, product.id, 200)   
    _event(db_session, EventType.ProductView, product.id, 1, token="someone-else")
    db_session.flush()

    rows = repo.user_events_for(
        db_session, user_id=None, session_token=GUEST,
        since=NOW - timedelta(days=90), event_types=WEIGHTED,
    )

    assert [(r.product_id, r.event_type) for r in rows] == [(product.id, EventType.ProductView)]


def test_history_without_owner_is_empty(db_session):
    assert repo.user_events_for(
        db_session, user_id=None, session_token=None,
        since=NOW - timedelta(days=90), event_types=WEIGHTED,
    ) == []


def test_counts_split_into_two_windows(db_session):
    product = _product(db_session, "reco-test-pop")
    for days in (2, 3, 20):
        _event(db_session, EventType.ProductView, product.id, days)
    _event(db_session, EventType.ProductView, product.id, 40)    # outside both windows
    db_session.flush()

    rows = {r.product_id: r for r in repo.event_counts(
        db_session,
        short_since=NOW - timedelta(days=7),
        long_since=NOW - timedelta(days=30),
        event_types=WEIGHTED,
    )}

    assert (rows[product.id].short_count, rows[product.id].long_count) == (2, 3)
