"""DoD M3: "white gold 585, ring, up to 3000 UAH" returns exactly the matching products."""
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.models.catalog import Category, Product, ProductVariant, VariantPrice
from app.models.enums import Currency, MetalColor, MetalType

DOD_QUERY = "/products?category=dod-rings&metal=Gold&color=White&fineness=585&price_max=3000"


def _product(db, category, slug, color, fineness, price, published=True):
    product = Product(
        category_id=category.id,
        slug=slug,
        published_at=datetime.now(timezone.utc) - timedelta(minutes=1) if published else None,
    )
    db.add(product)
    db.flush()
    variant = ProductVariant(
        product_id=product.id, sku=f"{slug}-1", metal_type=MetalType.Gold, metal_color=color,
        fineness=fineness, base_price=Decimal(price), stock_quantity=1,
    )
    db.add(variant)
    db.flush()
    db.add(VariantPrice(variant_id=variant.id, currency=Currency.UAH, price=Decimal(price)))
    db.flush()


def test_dod_filter_white_gold_585_ring_under_3000(client, db_session):
    # Unique slugs keep the test independent of seed data in the same DB
    rings = Category(slug="dod-rings")
    earrings = Category(slug="dod-earrings")
    db_session.add_all([rings, earrings])
    db_session.flush()

    _product(db_session, rings, "dod-match", MetalColor.White, 585, "2790")
    _product(db_session, rings, "dod-too-expensive", MetalColor.White, 585, "3500")
    _product(db_session, rings, "dod-yellow", MetalColor.Yellow, 585, "2500")
    _product(db_session, rings, "dod-750", MetalColor.White, 750, "2500")
    _product(db_session, rings, "dod-draft", MetalColor.White, 585, "2000", published=False)
    _product(db_session, earrings, "dod-earrings", MetalColor.White, 585, "2000")

    response = client.get(DOD_QUERY)
    assert response.status_code == 200, response.text
    items = response.json()["items"]
    assert [i["slug"] for i in items] == ["dod-match"]
    assert Decimal(items[0]["price_from"]) <= 3000
