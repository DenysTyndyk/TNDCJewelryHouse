from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.models.catalog import Category, Product, ProductEmbedding, ProductTranslation
from app.models.enums import SearchType
from app.models.telemetry import SearchQuery
from app.repositories import search_repository as repo
from scripts.build_embeddings import UPDATE_SEARCH_VECTOR

DIM = 384


def _unit(i: int) -> list[float]:
    vec = [0.0] * DIM
    vec[i] = 1.0
    return vec


def _product(db, slug, name, description):
    category = Category(slug=f"{slug}-cat")
    db.add(category)
    db.flush()
    product = Product(
        category_id=category.id, slug=slug,
        published_at=datetime.now(timezone.utc) - timedelta(days=1),
    )
    db.add(product)
    db.flush()
    db.add(ProductTranslation(product_id=product.id, locale="uk", name=name, description=description))
    db.flush()
    return product


def _embedding(db, product, locale, vec):
    db.add(ProductEmbedding(
        product_id=product.id, locale=locale, model_name=settings.embedding_model,
        content_hash="test", embedding=vec,
    ))
    db.flush()


def test_lexical_finds_word_and_ignores_diacritics(db_session):
    product = _product(db_session, "lex-test", "Pierścionek Zqxvyt", "Złoty pierścionek")
    db_session.execute(UPDATE_SEARCH_VECTOR, {"ids": [product.id]})

    assert product.id in repo.lexical(db_session, "zqxvyt")
    assert product.id in repo.lexical(db_session, "zloty pierscionek")
    assert product.id not in repo.lexical(db_session, "srebro zqxvyt-nothing")


def test_semantic_nearest_first_and_grouped_by_product(db_session):
    near = _product(db_session, "sem-near", "A", "A")
    far = _product(db_session, "sem-far", "B", "B")
    _embedding(db_session, near, "uk", _unit(0))
    _embedding(db_session, near, "pl", _unit(1))
    _embedding(db_session, far, "uk", _unit(2))

    ranked = repo.semantic(db_session, _unit(1))

    assert ranked[0] == near.id
    assert ranked.count(near.id) == 1  


def test_cached_query_embedding_returns_latest(db_session):
    text_q = "cache-test-query-xyz"
    for vec in (_unit(0), _unit(5)):
        db_session.add(SearchQuery(
            query_text=text_q, search_type=SearchType.Semantic, query_embedding=vec,
        ))
        db_session.flush()

    assert repo.cached_query_embedding(db_session, text_q) == _unit(5)
    assert repo.cached_query_embedding(db_session, "never-searched-xyz") is None