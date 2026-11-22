import math
from collections import defaultdict
from datetime import datetime


from app.models.enums import EventType

EVENT_WEIGHTS: dict[EventType, float] = {
    EventType.ProductView: 1.0,
    EventType.Search: 1.0,
    EventType.ClickRecommendation: 2.0,
    EventType.AddToFavorites: 3.0,
    EventType.AddToCart: 4.0,
    EventType.Purchase: 6.0,
}

def score(events, now: datetime, decay_lambda: float) -> dict[int, float]:
    scores: dict[int, float] = defaultdict(float)
    for product_id, event_type, created_at in events:
        weight = EVENT_WEIGHTS.get(event_type)
        if weight is None:  
            continue
        days = max((now - created_at).total_seconds() / 86400, 0.0)  
        scores[product_id] += weight * math.exp(-decay_lambda * days)
    return dict(scores)