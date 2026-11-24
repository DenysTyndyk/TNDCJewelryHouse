import logging
from dataclasses import dataclass
from typing import Literal

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.enums import SearchType
from app.models.telemetry import SearchQuery
from app.repositories import catalog_repository, search_repository
from app.schemas.catalog import ProductFilter
from app.services.catalog_service import CURRENCY
from app.services.search.embedder_client import EmbedderUnavailable, embed

logger = logging.getLogger(__name__)
Mode = Literal["lexical", "semantic", "hybrid"]

MAX_QUERY_LENGTH = 500
CANDIDATES = 100 

@dataclass
class SearchResult:
    mode_used: Mode
    total: int
    ids: list[int]

def normalize_query(q: str)-> str:
    return q.strip().lower()[:MAX_QUERY_LENGTH]

def rrf(rankings: list[list[int]], k: int = 60) -> list[int]:
    scores: dict[int,float] = {}
    for ranking in rankings:
        for rank, product_id in enumerate(ranking, start=1):
            scores[product_id] = scores.get(product_id,0.0) + 1.0 / (k+rank)
    return sorted(scores,key=lambda pid: (-scores[pid], pid))


def _query_vector(db: Session, q: str) -> list[float] | None:
    cached = search_repository.cached_query_embedding(db, q)
    if cached is not None:
        return cached
    try:
        return embed([q], "query")[0]
    except EmbedderUnavailable as exc:
        logger.warning("Embedder unavailable, falling back to lexical search: %s", exc)
        return None

def rank(db: Session, q: str, mode: Mode, qvec: list[float] | None) -> list[int]:
    if mode == "lexical":
        return search_repository.lexical(db, q, CANDIDATES)
    if mode == "semantic":
        return search_repository.semantic(db, qvec, CANDIDATES)
    return rrf(
        [search_repository.lexical(db, q, CANDIDATES), search_repository.semantic(db, qvec, CANDIDATES)],
        k=settings.search_rrf_k,
    )

def search(
    db: Session,
    q: str,
    mode: Mode,
    filters: ProductFilter,
    locale: str,
    *,
    offset: int = 0,
    user_id: int | None,
    session_token: str | None,
    tracking: bool,
) -> SearchResult:
    q = normalize_query(q)

    qvec = None
    if mode != "lexical" and settings.semantic_search_enabled:
        qvec = _query_vector(db, q)
    mode_used: Mode = mode if qvec is not None else "lexical"

    ranked = rank(db, q, mode_used, qvec)

    matched: list[int] = []
    if ranked:
        sql_filters = filters.model_copy(update={"locale": locale, "cursor": None})
        rows, _ = catalog_repository.list_products(db, sql_filters, CURRENCY, ids=ranked)
        allowed = {r.id for r in rows}
        matched = [pid for pid in ranked if pid in allowed]

    db.add(
        SearchQuery(
            query_text=q,
            locale=locale,
            results_count=len(matched),
            search_type=SearchType(mode_used.capitalize()),
            query_embedding=qvec,
            user_id=user_id if tracking else None,
            session_token=session_token if tracking else None,
        )
    )
    db.flush()

    return SearchResult(
        mode_used=mode_used,
        total=len(matched),
        ids=matched[offset : offset + filters.limit],
    )