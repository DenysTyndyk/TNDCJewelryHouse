from collections import defaultdict

from sqlalchemy import func, select, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_session
from app.models.catalog import (
    CategoryTranslation, Gemstone, Product, ProductEmbedding,
    ProductGemstone, ProductTranslation, ProductVariant,
)
from app.repositories.catalog_repository import IS_PUBLISHED
from app.services.search.embedder_client import EmbedderUnavailable, embed
from app.services.search.passage import build_passage, content_hash

LOCALES = ("uk", "pl", "en")
BATCH_SIZE = 32
EMBED_TIMEOUT_S = 60.0

UPDATE_SEARCH_VECTOR = text("""
    UPDATE products p SET search_vector = (
        SELECT setweight(to_tsvector('tndc_search', coalesce(string_agg(t.name, ' '), '')), 'A')
            || setweight(to_tsvector('tndc_search', coalesce(string_agg(t.description, ' '), '')), 'B')
        FROM product_translations t
        WHERE t.product_id = p.id
    )
    WHERE p.id = ANY(CAST(:ids AS bigint[])) OR p.search_vector IS NULL
""")

def _pending(db: Session) -> tuple[int, list[tuple[int, str, str, str]]]:
    published = select(Product.id).where(IS_PUBLISHED)

    variants = defaultdict(list)
    for v in db.scalars(select(ProductVariant).where(ProductVariant.product_id.in_(published))):
        variants[v.product_id].append(v)

    gems = defaultdict(list)
    rows = db.execute(
        select(ProductGemstone.product_id,Gemstone.slug)
        .join(Gemstone,Gemstone.id == ProductGemstone.gemstone_id)
        .where(ProductGemstone.product_id.in_(published))
    )
    for product_id, slug in rows:
        gems[product_id].append(slug)

    category_names = {
        (c.category_id, c.locale): c.name
        for c in db.scalars(select(CategoryTranslation).where(CategoryTranslation.locale.in_(LOCALES)))
    }
    existing = {
        (pid, locale): h
        for pid, locale, h in db.execute(
            select(ProductEmbedding.product_id, ProductEmbedding.locale, ProductEmbedding.content_hash)
            .where(ProductEmbedding.model_name == settings.embedding_model)
        )
    }
    translations = db.execute(
        select(ProductTranslation, Product.category_id)
        .join(Product, Product.id == ProductTranslation.product_id)
        .where(IS_PUBLISHED, ProductTranslation.locale.in_(LOCALES))
    ).all()

    pending = []
    for t, category_id in translations:
        pid = t.product_id
        category = category_names.get((category_id, t.locale), "")
        passage = build_passage(t, category, variants[pid], gems[pid], t.locale)
        h = content_hash(passage)
        if existing.get((pid, t.locale)) != h:
            pending.append((pid, t.locale, passage, h))
    return len(translations), pending

def run(db: Session, embed_fn=embed) -> tuple[int, int, int]:
    checked, pending = _pending(db)

    db.execute(UPDATE_SEARCH_VECTOR, {"ids": sorted({p[0] for p in pending})})
    db.commit()

    for start in range(0, len(pending), BATCH_SIZE):
        batch = pending[start:start + BATCH_SIZE]
        vectors = embed_fn([p[2] for p in batch], "passage", timeout=EMBED_TIMEOUT_S)
        stmt = insert(ProductEmbedding).values([
            {
                "product_id": pid,
                "locale": locale,
                "model_name": settings.embedding_model,
                "embedding_version": settings.embedding_version,
                "content_hash": h,
                "embedding": vec,
            }
            for (pid, locale, _, h), vec in zip(batch, vectors)
        ])
        db.execute(stmt.on_conflict_do_update(
            index_elements=["product_id", "locale", "model_name"],
            set_={
                "embedding": stmt.excluded.embedding,
                "content_hash": stmt.excluded.content_hash,
                "embedding_version": stmt.excluded.embedding_version,
                "updated_at": func.now(),
            },
        ))
        db.commit() 

    return checked, len(pending), checked - len(pending)


def main() -> None:
    db = get_session()
    try:
        checked, embedded, skipped = run(db)
    except EmbedderUnavailable as exc:
        raise SystemExit(f"embedder unavailable, search_vector updated, embeddings retried next pass: {exc}")
    finally:
        db.close()
    print(f"checked={checked}, embedded={embedded}, skipped={skipped}")


if __name__ == "__main__":
    main()