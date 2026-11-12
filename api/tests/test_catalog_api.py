"""Public catalog API: cursor pagination, filters, translation fallback, unpublished products."""
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.models.catalog import Category, Product, ProductTranslation, ProductVariant, VariantPrice
from app.models.enums import Currency, MetalType


def _now():
    return datetime.now(timezone.utc)


def _category(db, slug, parent=None):
    category = Category(slug=slug, parent_id=parent.id if parent else None)
    db.add(category)
    db.flush()
    return category


def _product(db, category, slug, price="1000", sale=None, sale_ends_at=None,
             published_at=..., names=None):
    product = Product(
        category_id=category.id,
        slug=slug,
        # func.now() is the transaction start time, so "published" must lie in the past
        published_at=_now() - timedelta(minutes=5) if published_at is ... else published_at,
    )
    db.add(product)
    db.flush()
    for locale, name in (names or {}).items():
        db.add(ProductTranslation(product_id=product.id, locale=locale, name=name))
    variant = ProductVariant(
        product_id=product.id, sku=f"{slug}-1", metal_type=MetalType.Gold,
        fineness=585, base_price=Decimal(price), stock_quantity=1,
    )
    db.add(variant)
    db.flush()
    db.add(VariantPrice(
        variant_id=variant.id, currency=Currency.UAH, price=Decimal(price),
        sale_price=Decimal(sale) if sale else None, sale_ends_at=sale_ends_at,
    ))
    db.flush()
    return product


def _slugs(response):
    assert response.status_code == 200, response.text
    return [i["slug"] for i in response.json()["items"]]


# —— cursor pagination ——


def test_cursor_pages_do_not_overlap(client, db_session):
    cat = _category(db_session, "t-page")
    for i in range(5):
        _product(db_session, cat, f"t-page-{i}", published_at=_now() - timedelta(minutes=10 + i))

    seen, cursor = [], None
    for _ in range(3):
        url = "/products?category=t-page&limit=2" + (f"&cursor={cursor}" if cursor else "")
        response = client.get(url)
        seen += _slugs(response)
        cursor = response.json()["next_cursor"]

    assert seen == [f"t-page-{i}" for i in range(5)]  # newest first, no duplicates, nothing lost
    assert cursor is None


def test_cursor_pagination_by_price(client, db_session):
    cat = _category(db_session, "t-price-page")
    for i, price in enumerate(["300", "100", "200"]):
        _product(db_session, cat, f"t-pp-{i}", price=price)

    first = client.get("/products?category=t-price-page&sort=price_asc&limit=2")
    second = client.get(f"/products?category=t-price-page&sort=price_asc&limit=2"
                        f"&cursor={first.json()['next_cursor']}")
    assert _slugs(first) == ["t-pp-1", "t-pp-2"]
    assert _slugs(second) == ["t-pp-0"]


def test_invalid_cursor_returns_400(client):
    for cursor in ("garbage", "W10=", "WyJub3QtYS1kYXRlIiwgMV0="):  # not b64, [], ["not-a-date", 1]
        assert client.get(f"/products?cursor={cursor}").status_code == 400, cursor


# —— filters ——


def test_category_filter_includes_subcategories(client, db_session):
    rings = _category(db_session, "t-rings")
    wedding = _category(db_session, "t-wedding", parent=rings)
    other = _category(db_session, "t-other")
    _product(db_session, rings, "t-ring")
    _product(db_session, wedding, "t-wedding-ring")
    _product(db_session, other, "t-other-item")

    assert sorted(_slugs(client.get("/products?category=t-rings"))) == ["t-ring", "t-wedding-ring"]
    assert _slugs(client.get("/products?category=t-wedding")) == ["t-wedding-ring"]


def test_price_filter_uses_active_sale_price(client, db_session):
    cat = _category(db_session, "t-sale")
    _product(db_session, cat, "t-on-sale", price="4000", sale="2500")
    _product(db_session, cat, "t-sale-expired", price="4000", sale="2500",
             sale_ends_at=_now() - timedelta(days=1))

    response = client.get("/products?category=t-sale&price_max=3000")
    assert _slugs(response) == ["t-on-sale"]
    item = response.json()["items"][0]
    assert Decimal(item["price_from"]) == Decimal("2500")
    assert item["has_sale"] is True


def test_price_min_greater_than_max_returns_422(client):
    assert client.get("/products?price_min=5000&price_max=1000").status_code == 422


# —— translations ——


def test_translation_falls_back_to_uk(client, db_session):
    cat = _category(db_session, "t-tr")
    _product(db_session, cat, "t-tr-uk-only", names={"uk": "Каблучка"})
    _product(db_session, cat, "t-tr-both", names={"uk": "Сережки", "pl": "Kolczyki"})

    assert client.get("/products/t-tr-uk-only?locale=pl").json()["name"] == "Каблучка"
    assert client.get("/products/t-tr-both?locale=pl").json()["name"] == "Kolczyki"
    listing = {i["slug"]: i["name"] for i in client.get("/products?category=t-tr&locale=en").json()["items"]}
    assert listing == {"t-tr-uk-only": "Каблучка", "t-tr-both": "Сережки"}


# —— unpublished ——


def test_unpublished_product_returns_404(client, db_session):
    cat = _category(db_session, "t-hidden")
    _product(db_session, cat, "t-draft", published_at=None)
    _product(db_session, cat, "t-scheduled", published_at=_now() + timedelta(days=1))

    assert client.get("/products/t-draft").status_code == 404
    assert client.get("/products/t-scheduled").status_code == 404
    assert client.get("/products/t-does-not-exist").status_code == 404
    assert _slugs(client.get("/products?category=t-hidden")) == []
