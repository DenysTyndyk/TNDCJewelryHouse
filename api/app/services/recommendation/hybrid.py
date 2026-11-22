from datetime import datetime

def _scale(scores: dict[int,float]) -> dict[int,float]:
    top = max(scores.values(),default=0.0)
    return {k: v/top for k, v in scores.items()} if top > 0 else scores

def novelty(published_at: dict[int, datetime]) -> dict[int,float]:
    if not published_at:
        return {}
    oldest,newest = min(published_at.values()), max(published_at.values())
    span = (newest - oldest).total_seconds()
    if not span: 
        return {pid: 1.0 for pid in published_at}
    return {pid: (ts - oldest).total_seconds() / span for pid, ts in published_at.items()}

def combine(
        candidates,
        *,
         behavior: dict[int, float],
        content: dict[int, float],
    popularity: dict[int, float],
    novelty: dict[int, float],
    a: float,
    b: float,
    c: float,
    d: float,
) -> list[tuple[int, float]]:
    behavior, content, popularity, novelty = map(_scale, (behavior, content, popularity, novelty))
    scored = [
        (
            pid,
            a * behavior.get(pid, 0.0)
            + b * content.get(pid, 0.0)
            + c * popularity.get(pid, 0.0)
            + d * novelty.get(pid, 0.0),
        )
        for pid in candidates
    ]
    scored.sort(key=lambda p: p[1], reverse=True)
    return scored