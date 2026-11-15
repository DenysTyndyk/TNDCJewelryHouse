from io import BytesIO

import pytest
from PIL import Image
from sqlalchemy import select

from app.core.security import create_access_token
from app.models.catalog import Gemstone, PriceHistory
from app.models.enums import Role
from app.repositories import user_repository as user_repo
from app.services import admin_catalog_service as svc


def _png(width=2000, height=1000, with_gps=False) -> bytes:
    img = Image.new("RGB", (width, height), "gold")
    exif = Image.Exif()
    if with_gps:
        exif[0x8825] = {2: (50.0, 27.0, 0.0)}  
    buf = BytesIO()
    img.save(buf, "PNG", exif=exif)
    return buf.getvalue()


def _auth(db_session, role: Role) -> dict:
    user = user_repo.create_user(db_session, f"{role.value.lower()}@admin-test.com", "not-a-real-hash")
    user.role = role
    db_session.flush()
    return {"Authorization": f"Bearer {create_access_token(user.id, role.value)}"}


# —— image processing (no DB) ——


def test_process_image_makes_three_webp_sizes_without_exif():
    files, width, height = svc.process_image(_png(with_gps=True))
    assert set(files) == {400, 800, 1600}
    assert (width, height) == (1600, 800)
    for target, data in files.items():
        out = Image.open(BytesIO(data))
        assert out.format == "WEBP"
        assert out.width == target
        assert not out.getexif()  


def test_process_image_never_upscales():
    files, width, _ = svc.process_image(_png(width=300, height=300))
    assert width == 300
    assert Image.open(BytesIO(files[1600])).width == 300


def test_process_image_rejects_non_image():
    with pytest.raises(svc.InvalidImageError):
        svc.process_image(b"<?php echo 'not an image'; ?>")


# —— access control ——


def test_admin_requires_token(client):
    assert client.post("/admin/products", json={}).status_code == 401


def test_admin_forbidden_for_regular_user(client, db_session):
    headers = _auth(db_session, Role.User)
    assert client.post("/admin/products", json={}, headers=headers).status_code == 403


# —— full flow as Manager ——


def test_manager_builds_product_end_to_end(client, db_session, tmp_path, monkeypatch):
    monkeypatch.setattr(svc, "MEDIA_DIR", tmp_path)
    h = _auth(db_session, Role.Manager)

    cat = client.post("/admin/categories", headers=h, json={
        "slug": "admin-test-rings", "translations": {"uk": {"name": "Каблучки"}},
    })
    assert cat.status_code == 201, cat.text

    product = client.post("/admin/products", headers=h, json={
        "category_id": cat.json()["id"], "slug": "admin-test-ring",
    })
    assert product.status_code == 201, product.text
    pid = product.json()["id"]
    assert client.post("/admin/products", headers=h, json={
        "category_id": cat.json()["id"], "slug": "admin-test-ring",
    }).status_code == 409  # duplicate slug

    tr = client.put(f"/admin/products/{pid}/translations/uk", headers=h, json={"name": "Каблучка"})
    assert tr.status_code == 200, tr.text

    variant = client.post(f"/admin/products/{pid}/variants", headers=h, json={
        "sku": "ADMIN-TEST-1", "metal_type": "Gold", "fineness": 585, "base_price": "10000",
    })
    assert variant.status_code == 201, variant.text
    vid = variant.json()["id"]

    for amount in ("12000", "12000", "11500"):  # repeating the same price must not log history
        r = client.put(f"/admin/variants/{vid}/price", headers=h, json={"price": amount})
        assert r.status_code == 200, r.text
    history = db_session.scalars(select(PriceHistory.price).where(PriceHistory.variant_id == vid)).all()
    assert sorted(str(p) for p in history) == ["11500.00", "12000.00"]

    gem = Gemstone(slug="admin-test-ruby", name="Ruby")
    db_session.add(gem)
    db_session.flush()
    link = client.post(f"/admin/products/{pid}/gemstones", headers=h, json={"gemstone_id": gem.id})
    assert link.status_code == 201, link.text

    upload = client.post(
        f"/admin/products/{pid}/images", headers=h,
        files={"file": ("ring.png", _png(), "image/png")}, data={"is_primary": "true"},
    )
    assert upload.status_code == 201, upload.text
    image = upload.json()
    assert (image["width"], image["height"]) == (1600, 800)
    paths = svc.image_paths(image["storage_key"])
    assert all(p.exists() for p in paths)

    fake = client.post(
        f"/admin/products/{pid}/images", headers=h,
        files={"file": ("evil.jpg", b"not an image", "image/jpeg")},
    )
    assert fake.status_code == 422

    assert client.delete(f"/admin/images/{image['id']}", headers=h).status_code == 204
    assert not any(p.exists() for p in paths)

    assert client.patch(f"/admin/products/{pid}", headers=h, json={"published_at": None}).status_code == 200
    assert client.delete(f"/admin/products/{pid}", headers=h).status_code == 204
