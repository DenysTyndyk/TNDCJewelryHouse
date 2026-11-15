"""Admin catalog use cases: CRUD, prices with history (Omnibus), image upload to WebP."""
import uuid
from contextlib import contextmanager
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import MEDIA_DIR
from app.models.catalog import (
    Category,
    Gemstone,
    PriceHistory,
    Product,
    ProductGemstone,
    ProductImage,
    ProductVariant,
    VariantPrice,
)
from app.repositories import admin_catalog_repository as repo
from app.schemas.admin_catalog import (
    CategoryCreate,
    CategoryUpdate,
    PriceIn,
    ProductCreate,
    ProductGemstoneIn,
    ProductTranslationIn,
    ProductUpdate,
    VariantCreate,
    VariantUpdate,
)

IMAGE_WIDTHS = (400, 800, 1600)
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
MAX_PIXELS = 40_000_000  # ~6300×6300; stops "decompression bomb" uploads before decoding
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}


class NotFoundError(Exception):
    pass


class ConflictError(Exception):
    pass


class InvalidImageError(Exception):
    pass


@contextmanager
def _tx(db: Session):
    """Commit the block; turn unique/FK/check violations into ConflictError (HTTP 409)."""
    try:
        yield
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError(str(exc.orig).split("\n")[0]) from exc


def _get(db: Session, model, obj_id: int):
    obj = db.get(model, obj_id)
    if obj is None:
        raise NotFoundError(f"{model.__name__} {obj_id} not found")
    return obj


def _apply(obj, data: dict):
    for field, value in data.items():
        setattr(obj, field, value)


# --- categories ---

def _check_parent(db: Session, category_id: int | None, parent_id: int | None) -> None:
    """Parent must exist and must not be the category itself or one of its descendants (cycle)."""
    current = parent_id
    while current is not None:
        if current == category_id:
            raise ConflictError("Category cannot be its own ancestor")
        current = _get(db, Category, current).parent_id


def create_category(db: Session, data: CategoryCreate) -> Category:
    _check_parent(db, None, data.parent_id)
    category = Category(**data.model_dump(exclude={"translations"}))
    with _tx(db):
        db.add(category)
        db.flush()  # need category.id for translations
        for locale, tr in data.translations.items():
            repo.upsert_category_translation(db, category.id, locale, tr.model_dump())
    db.refresh(category)
    return category


def update_category(db: Session, category_id: int, data: CategoryUpdate) -> Category:
    category = _get(db, Category, category_id)
    fields = data.model_dump(exclude_unset=True, exclude={"translations"})
    if "parent_id" in fields:
        _check_parent(db, category_id, fields["parent_id"])
    with _tx(db):
        _apply(category, fields)
        for locale, tr in (data.translations or {}).items():
            repo.upsert_category_translation(db, category_id, locale, tr.model_dump())
    db.refresh(category)
    return category


# --- products ---

def create_product(db: Session, data: ProductCreate) -> Product:
    _get(db, Category, data.category_id)
    product = Product(**data.model_dump())
    with _tx(db):
        db.add(product)
    db.refresh(product)
    return product


def update_product(db: Session, product_id: int, data: ProductUpdate) -> Product:
    product = _get(db, Product, product_id)
    fields = data.model_dump(exclude_unset=True)
    if fields.get("category_id") is not None:
        _get(db, Category, fields["category_id"])
    with _tx(db):
        _apply(product, fields)
    db.refresh(product)
    return product


def delete_product(db: Session, product_id: int) -> None:
    product = _get(db, Product, product_id)
    keys = repo.list_image_keys(db, product_id)
    with _tx(db):  # 409 if the product is referenced by orders; unpublish it instead
        db.delete(product)
    _delete_files(keys)  # image rows are removed by ON DELETE CASCADE, files are not


def set_product_translation(db: Session, product_id: int, locale: str, data: ProductTranslationIn):
    _get(db, Product, product_id)
    with _tx(db):
        tr = repo.upsert_product_translation(db, product_id, locale, data.model_dump())
    db.refresh(tr)
    return tr


# --- variants and prices ---

def create_variant(db: Session, product_id: int, data: VariantCreate) -> ProductVariant:
    _get(db, Product, product_id)
    variant = ProductVariant(product_id=product_id, **data.model_dump())
    with _tx(db):
        db.add(variant)
    db.refresh(variant)
    return variant


def update_variant(db: Session, variant_id: int, data: VariantUpdate) -> ProductVariant:
    variant = _get(db, ProductVariant, variant_id)
    with _tx(db):
        _apply(variant, data.model_dump(exclude_unset=True))
    db.refresh(variant)
    return variant


def delete_variant(db: Session, variant_id: int) -> None:
    variant = _get(db, ProductVariant, variant_id)
    with _tx(db):
        db.delete(variant)


def set_price(db: Session, variant_id: int, data: PriceIn) -> VariantPrice:
    """Upsert the variant's price in one currency; every change of `price` lands in price_history."""
    _get(db, ProductVariant, variant_id)
    price = repo.get_price(db, variant_id, data.currency)
    changed = price is None or price.price != data.price
    with _tx(db):
        if price is None:
            price = VariantPrice(variant_id=variant_id)
            db.add(price)
        _apply(price, data.model_dump())
        if changed:
            # shortcut: only the regular price is logged, not sale_price; extend when Omnibus display (PL) is built
            db.add(PriceHistory(variant_id=variant_id, currency=data.currency, price=data.price))
    db.refresh(price)
    return price


# --- gemstones ---

def _check_variant_of(db: Session, product_id: int, variant_id: int | None) -> None:
    if variant_id is not None and _get(db, ProductVariant, variant_id).product_id != product_id:
        raise NotFoundError(f"ProductVariant {variant_id} not found in product {product_id}")


def add_gemstone(db: Session, product_id: int, data: ProductGemstoneIn) -> ProductGemstone:
    _get(db, Product, product_id)
    _get(db, Gemstone, data.gemstone_id)
    _check_variant_of(db, product_id, data.variant_id)
    link = ProductGemstone(product_id=product_id, **data.model_dump())
    with _tx(db):
        db.add(link)
    db.refresh(link)
    return link


def remove_gemstone(db: Session, product_id: int, link_id: int) -> None:
    link = _get(db, ProductGemstone, link_id)
    if link.product_id != product_id:
        raise NotFoundError(f"ProductGemstone {link_id} not found in product {product_id}")
    with _tx(db):
        db.delete(link)


# --- images ---

def image_paths(storage_key: str) -> list[Path]:
    """Uploaded images are stored as {key}-400.webp, {key}-800.webp, {key}-1600.webp."""
    return [MEDIA_DIR / f"{storage_key}-{w}.webp" for w in IMAGE_WIDTHS]


def _delete_files(keys: list[str]) -> None:
    for key in keys:
        for path in image_paths(key):
            path.unlink(missing_ok=True)


def process_image(data: bytes) -> tuple[dict[int, bytes], int, int]:
    """Validate an upload by its content (not extension) and render WebP copies without metadata.

    Returns ({target_width: webp_bytes}, width, height) where width/height are of the largest copy.
    """
    try:
        img = Image.open(BytesIO(data))
        if img.format not in ALLOWED_FORMATS:
            raise InvalidImageError(f"Unsupported image format: {img.format}")
        if img.width * img.height > MAX_PIXELS:
            raise InvalidImageError("Image resolution is too large")
        img.load()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise InvalidImageError("File is not a valid image") from exc

    img = ImageOps.exif_transpose(img)  # apply camera rotation before EXIF is dropped
    has_alpha = "A" in img.getbands() or "transparency" in img.info
    img = img.convert("RGBA" if has_alpha else "RGB")
    # Drop EXIF/XMP (may contain GPS location); keep only the colour profile
    img.info = {"icc_profile": img.info["icc_profile"]} if "icc_profile" in img.info else {}

    files: dict[int, bytes] = {}
    for width in IMAGE_WIDTHS:
        copy = img.copy()
        copy.thumbnail((width, img.height))  # limit width only; never upscales
        buf = BytesIO()
        copy.save(buf, "WEBP", quality=82, method=4, icc_profile=img.info.get("icc_profile"))
        files[width] = buf.getvalue()
    return files, copy.width, copy.height


def save_image(storage_key: str, data: bytes) -> tuple[int, int]:
    """Validate the image, write its WebP copies under `storage_key` and return (width, height)."""
    files, width, height = process_image(data)
    paths = image_paths(storage_key)
    paths[0].parent.mkdir(parents=True, exist_ok=True)
    for target, path in zip(IMAGE_WIDTHS, paths):
        path.write_bytes(files[target])
    return width, height


def upload_image(db: Session, product_id: int, data: bytes, alt_text: str | None, is_primary: bool) -> ProductImage:
    _get(db, Product, product_id)
    key = f"products/{product_id}/{uuid.uuid4().hex}"
    width, height = save_image(key, data)

    image = ProductImage(
        product_id=product_id, storage_key=key, alt_text=alt_text,
        width=width, height=height, is_primary=is_primary,
    )
    try:
        with _tx(db):
            if is_primary:
                repo.clear_primary_image(db, product_id)
            db.add(image)
    except ConflictError:
        _delete_files([key])  # do not leave orphan files when the row was not saved
        raise
    db.refresh(image)
    return image


def delete_image(db: Session, image_id: int) -> None:
    image = _get(db, ProductImage, image_id)
    key = image.storage_key
    with _tx(db):
        db.delete(image)
    _delete_files([key])
