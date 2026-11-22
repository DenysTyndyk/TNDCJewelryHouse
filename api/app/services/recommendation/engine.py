from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.core.config import settings
from app.repositories import recommendation_repository as repo
from app.services.recommendation import behavior, content_based, hybrid, popularity, rules

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

def similar(db: Session, product_id: int, *, user_id: int | None, session_token: str | None) -> list[int]:
    features = repo.load_product_features(db)
    categories = {f.id: f.category_id for f in features}
    if product_id not in categories:
        raise ProductNotFoundError(product_id)
    vectors = content_based.build_vectors(features)
    ranked = content_based.similar(vectors, categories, product_id, k=len(vectors))
    purchased = repo.purchased_product_ids(db, user_id=user_id, session_token=session_token)
    picked = rules.apply_rules(
        ranked,
        available={f.id for f in features if f.available},
        exclude=purchased | {product_id},
        category=categories,
        limit=settings.reco_limit,
        max_per_category=settings.reco_limit,
    )
    return [pid for pid, _ in picked]

def for_you(
    db: Session, *, user_id: int | None, session_token: str | None, tracking: bool
) -> tuple[str, list[int]]:
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