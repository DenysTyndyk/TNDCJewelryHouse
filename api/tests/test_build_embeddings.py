from datetime import datetime, timedelta, timezone

from app.models.catalog import Category, Product, ProductTranslation
from scripts import build_embeddings


def fake_embed(texts, kind, timeout=None):
    assert kind == "passage"
    return [[0.0] * 383 + [1.0] for _ in texts]


def test_only_changed_pairs_are_reembedded(db_session):
    category = Category(slug="emb-test-cat")
    db_session.add(category)
    db_session.flush()
    product = Product(
        category_id=category.id,
        slug="emb-test-ring",
        published_at=datetime.now(timezone.utc) - timedelta(days=1),
    )
    db_session.add(product)
    db_session.flush()
    tr = ProductTranslation(
        product_id=product.id, locale="uk", name="Каблучка", description="Золота каблучка"
    )
    db_session.add(tr)
    db_session.flush()

    build_embeddings.run(db_session, embed_fn=fake_embed)  # first pass may also embed seed data
    assert build_embeddings.run(db_session, embed_fn=fake_embed)[1] == 0

    tr.description = "Срібна каблучка"
    db_session.flush()
    assert build_embeddings.run(db_session, embed_fn=fake_embed)[1] == 1

    db_session.refresh(product)
    assert product.search_vector is not None