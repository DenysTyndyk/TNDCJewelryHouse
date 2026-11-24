from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.telemetry import SearchQuery
from app.models.catalog import ProductEmbedding

SEMANTIC_POOL = 300

LEXICAL_SQL = text("""
    SELECT p.id
    FROM products p, websearch_to_tsquery('tndc_search', :q) AS query
    WHERE p.search_vector @@ query
    ORDER BY ts_rank_cd(p.search_vector, query) DESC, p.id
    LIMIT :limit
""")

SEMANTIC_SQL = text("""
    SELECT product_id
    FROM (
        SELECT product_id, embedding <=> CAST(:qvec AS vector) AS distance
        FROM product_embeddings
        WHERE model_name = :model
        ORDER BY embedding <=> CAST(:qvec AS vector)
        LIMIT :pool
    ) nearest
    GROUP BY product_id
    ORDER BY min(distance), product_id
    LIMIT :limit
""")

def _vector_literal(vec: list[float]) -> str:
    return "[" + ",".join(str(float(x)) for x in vec) + "]"

def lexical(db: Session, q: str, limit: int = 100) -> list[int]:
    return list(db.scalars(LEXICAL_SQL, {"q": q, "limit": limit}))

def semantic(db: Session, qvec: list[float], limit: int = 100) -> list[int]:
    db.execute(text(f"SET LOCAL hnsw.ef_search = {SEMANTIC_POOL}"))
    params = {
        "qvec": _vector_literal(qvec),
        "model": settings.embedding_model,
        "pool": SEMANTIC_POOL,
        "limit": limit,
    }
    return list(db.scalars(SEMANTIC_SQL, params))

def cached_query_embedding(db: Session, normalized_q: str) -> list[float] | None:
    stmt = (
        select(SearchQuery.query_embedding)
        .where(
            SearchQuery.query_text == normalized_q,
            SearchQuery.query_embedding.is_not(None),
        )
        .order_by(SearchQuery.created_at.desc(), SearchQuery.id.desc())
        .limit(1)
    )
    vec = db.scalar(stmt)
    return None if vec is None else [float(x) for x in vec]

def similar_by_vector(db: Session, product_id: int, limit: int = 100) -> list[int]:
    source = db.scalar(
        select(ProductEmbedding.embedding).where(
            ProductEmbedding.product_id == product_id,
            ProductEmbedding.locale == "uk",
            ProductEmbedding.model_name == settings.embedding_model,
        )
    )
    if source is None:
        return []
    ranked = semantic(db, [float(x) for x in source], limit + 1)
    return [pid for pid in ranked if pid != product_id][:limit]