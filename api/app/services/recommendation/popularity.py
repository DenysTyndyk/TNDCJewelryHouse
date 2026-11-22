from datetime import datetime

SHORT_WEIGHT = 0.6
LONG_WEIGHT = 0.4

def score(
    counts,
    published_at: dict[int, datetime],
    now: datetime,
    short_days: int,
    long_days: int,
) -> dict[int, float]:
    raw: dict[int, float] = {}
    for product_id, short_count, long_count in counts:
        published = published_at.get(product_id)
        if published is None: 
            continue
        age = max((now - published).total_seconds() / 86400, 1.0)
        raw[product_id] = (
            SHORT_WEIGHT * short_count / min(age, short_days)
            + LONG_WEIGHT * long_count / min(age, long_days)
        )
    top = max(raw.values(), default=0.0)
    return {pid: v / top for pid, v in raw.items()} if top else raw