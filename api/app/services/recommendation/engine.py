from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.core.config import settings
from app.repositories import recommendation_repository as repo
from app.services.recommendation import behavior, content_based, hybrid, popularity, rules
from app.repositories import search_repository
from app.services.search.service import rrf

EVENT_TYPES = list(behavior.EVENT_WEIGHTS)


class ProductNotFoundError(Exception):
    pass

def _popularity(db:Session, published_at: dict, now: datetime) -> dict [int,float]:
    short_days= settings.reco_popularity_short_days
    long_days= settings.reco_popularity_long_days
    counts = repo.event_counts(
        db,
        short_since=now - timedelta(days=short_days),
        long_since = now - timedelta(days = long_days),
        event_types=EVENT_TYPES,
    ) 
    return popularity.score(counts, published_at, now, short_days, long_days)

def similar(
    db: Session,
    product_id: int,
    *,
    user_id: int | None,
    session_token: str | None,
    source: str | None = None,
) -> tuple[str, list[int]]:
    """source: "cbf" | "vector" | "hybrid"; None means settings.similar_source."""
    source = source or settings.similar_source
    features = repo.load_product_features(db)
    categories = {f.id: f.category_id for f in features}
    if product_id not in categories:
        raise ProductNotFoundError(product_id)

    def cbf() -> list[tuple[int, float]]:
        vectors = content_based.build_vectors(features)
        return content_based.similar(vectors, categories, product_id, k=len(vectors))

    vector = search_repository.similar_by_vector(db, product_id) if source != "cbf" else []
    if source == "vector" and vector:
        algorithm, ranked = "vector", [(pid, 0.0) for pid in vector]
    elif source == "hybrid" and vector:
        # Same RRF as hybrid search: fusing ranks needs no calibration between CBF scores and cosine distance.
        fused = rrf([vector, [pid for pid, _ in cbf()]], k=settings.search_rrf_k)
        algorithm, ranked = "hybrid", [(pid, 0.0) for pid in fused]
    else:  # cbf requested, or embeddings not built yet
        algorithm, ranked = "content", cbf()

    purchased = repo.purchased_product_ids(db, user_id=user_id, session_token=session_token)
    picked = rules.apply_rules(
        ranked,
        available={f.id for f in features if f.available},
        exclude=purchased | {product_id},
        category=categories,
        limit=settings.reco_limit,
        max_per_category=settings.reco_limit,
    )
    return algorithm, [pid for pid, _ in picked]

def _rank(db: Session, *, user_id: int | None, session_token: str | None, tracking: bool):
    """Full personal order of the catalog: hybrid with history, popularity without."""
    now = datetime.now(UTC)
    features = repo.load_product_features(db)
    categories = {f.id: f.category_id for f in features}
    published_at = {f.id: f.published_at for f in features}
    pop = _popularity(db, published_at, now)

    events = []
    if tracking:
        events = repo.user_events_for(db,user_id=user_id,session_token=session_token,since=now - timedelta(days=settings.reco_history_days),event_types=EVENT_TYPES)
    if events:
        algorithm = "hybrid"
        weights = behavior.score(events,now,settings.reco_decay_lambda)
        vectors = content_based.build_vectors(features)
        profile = content_based.profile_vector(weights, vectors)
        ranked = hybrid.combine(
            categories,
            behavior=weights,
            content={pid: content_based.cosine(profile, v) for pid, v in vectors.items()},
            popularity=pop,
            novelty=hybrid.novelty(published_at),
            a=settings.reco_weight_behavior,
            b=settings.reco_weight_content,
            c=settings.reco_weight_popularity,
            d=settings.reco_weight_novelty,
    )
    else :
        algorithm = "popularity"
        ranked = sorted(((pid, pop.get(pid, 0.0)) for pid in categories), key=lambda p: p[1], reverse=True)
    return algorithm, ranked, features, categories

def for_you(
    db: Session, *, user_id: int | None, session_token: str | None, tracking: bool
) -> tuple[str, list[int]]:
    algorithm, ranked, features, categories = _rank(
        db, user_id=user_id, session_token=session_token, tracking=tracking
    )
    picked = rules.apply_rules(
        ranked,
        available={f.id for f in features if f.available},
        exclude=(
            repo.purchased_product_ids(db, user_id=user_id, session_token=session_token)
            | repo.cart_product_ids(db, user_id=user_id, session_token=session_token)
        ),        
        category=categories,
        limit=settings.reco_limit,
        max_per_category=settings.reco_max_per_category,
    )
    return algorithm, [pid for pid, _ in picked]

def ranking(
    db: Session, *, user_id: int | None, session_token: str | None, tracking: bool
) -> tuple[str, list[int]]:
    """Personal order for catalog sort=recommended; no limit or rules, the catalog filters apply instead."""
    algorithm, ranked, _, _ = _rank(db, user_id=user_id, session_token=session_token, tracking=tracking)
    return algorithm, [pid for pid, _ in ranked]

def recently_viewed(
    db: Session, *, user_id: int | None, session_token: str | None, tracking: bool
) -> tuple[str, list[int]]:
    # Built from tracked views, so without consent there is nothing to show.
    if not tracking:
        return "history", []
    return "history", repo.recently_viewed(
        db, user_id=user_id, session_token=session_token, limit=settings.reco_limit
    )

def also_viewed(db: Session, product_id: int) -> tuple[str, list[int]]:
    since = datetime.now(UTC) - timedelta(days=settings.reco_history_days)
    return "co_view", repo.also_viewed(db, product_id, since=since, limit=settings.reco_limit)

def owner_key(user_id: int | None, session_token: str | None) -> str:
    return f"u{user_id}" if user_id is not None else f"s{session_token}"

def cached(db: Session, context: str, user_id: int | None, session_token: str | None, compute) -> tuple[str, list[int]]:
    owner = owner_key(user_id, session_token)
    key = f"{context}|{owner}"
    hit = repo.cache_get(db, key)
    if hit:
        return hit.algorithm, hit.product_ids
    algorithm, ids = compute()
    repo.cache_put(db, key, owner, algorithm, ids, settings.reco_cache_ttl_seconds)
    return algorithm, ids