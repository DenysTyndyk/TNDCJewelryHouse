import json
from io import BytesIO

from PIL import Image
from sqlalchemy import func, select

from app.models.catalog import (
    Category,
    Gemstone,
    PriceHistory,
    Product,
    ProductGemstone,
    ProductImage,
    ProductTranslation,
    ProductVariant,
)
from app.services import admin_catalog_service as svc
from scripts.import_products import import_all


def _png() -> bytes:
    buf = BytesIO()
    Image.new("RGB", (600, 800), "gold").save(buf, "PNG")
    return buf.getvalue()


def _folder(root, slug, data, photos=("1.png", "2.png")):
    folder = root / slug
    folder.mkdir()
    (folder / "product.json").write_text(json.dumps(data), encoding="utf-8")
    for name in photos:
        (folder / name).write_bytes(_png())


PRODUCT = {
    "category": "imp-earrings",
    "translations": {"uk": {"name": "Сережки"}, "pl": {"name": "Kolczyki"}},
    "variants": [{"sku": "IMP-1", "metal_type": "Gold", "metal_color": "Yellow", "fineness": 585,
                  "base_price": "9800", "stock_quantity": 3}],
    "gemstones": [{"gemstone": "imp-topaz", "quantity": 2, "is_center_stone": True}],
}


def _count(db, model, **where):
    return db.scalar(select(func.count()).select_from(model).filter_by(**where))


def test_import_creates_then_updates_without_duplicates(db_session, tmp_path, monkeypatch):
    monkeypatch.setattr(svc, "MEDIA_DIR", tmp_path / "media")
    db_session.add_all([Category(slug="imp-earrings"), Gemstone(slug="imp-topaz", name="Топаз")])
    db_session.flush()
    (tmp_path / "src").mkdir()
    _folder(tmp_path / "src", "imp-ring", PRODUCT)

    assert import_all(db_session, tmp_path / "src") == (1, [])
    product = db_session.scalar(select(Product).where(Product.slug == "imp-ring"))
    assert product.published_at is not None
    assert _count(db_session, ProductTranslation, product_id=product.id) == 2
    assert _count(db_session, ProductGemstone, product_id=product.id) == 1
    images = db_session.scalars(select(ProductImage).where(ProductImage.product_id == product.id)
                                .order_by(ProductImage.is_primary.desc())).all()
    assert [i.is_primary for i in images] == [True, False]
    assert all(p.exists() for p in svc.image_paths(images[0].storage_key))

    assert import_all(db_session, tmp_path / "src") == (1, [])  # second run updates in place
    assert _count(db_session, Product, slug="imp-ring") == 1
    assert _count(db_session, ProductVariant, product_id=product.id) == 1
    assert _count(db_session, ProductGemstone, product_id=product.id) == 1
    assert _count(db_session, ProductImage, product_id=product.id) == 2
    variant_id = db_session.scalar(select(ProductVariant.id).where(ProductVariant.sku == "IMP-1"))
    assert _count(db_session, PriceHistory, variant_id=variant_id) == 1  # same price → no new history row


def test_import_reports_bad_folder_and_continues(db_session, tmp_path, monkeypatch):
    monkeypatch.setattr(svc, "MEDIA_DIR", tmp_path / "media")
    db_session.add_all([Category(slug="imp-earrings"), Gemstone(slug="imp-topaz", name="Топаз")])
    db_session.flush()
    src = tmp_path / "src"
    src.mkdir()
    _folder(src, "imp-a-bad-category", {**PRODUCT, "category": "no-such-category"})
    _folder(src, "imp-b-no-photos", {**PRODUCT, "variants": [{**PRODUCT["variants"][0], "sku": "IMP-2"}]}, photos=())
    _folder(src, "imp-c-good", {**PRODUCT, "variants": [{**PRODUCT["variants"][0], "sku": "IMP-3"}]})

    imported, errors = import_all(db_session, src)
    assert imported == 1
    assert "no-such-category" in errors[0]
    assert "no photos" in errors[1]
    assert _count(db_session, Product, slug="imp-a-bad-category") == 0  # nothing half-written
