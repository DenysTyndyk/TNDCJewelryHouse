import json
import math
import sys
import time
from collections import defaultdict
from pathlib import Path
from statistics import mean

from sqlalchemy import select

from app.db.session import get_session
from app.models.catalog import Product
from app.services.search import service
from app.services.search.embedder_client import EmbedderUnavailable, embed

DEFAULT_QUERIES = Path("eval/search_queries.json") 
MODES = ("lexical", "semantic", "hybrid")
K = 10


def precision_at(ranked: list[int], relevant: set[int], k: int = 5) -> float:
    return sum(1 for pid in ranked[:k] if pid in relevant) / k


def mrr_at(ranked: list[int], relevant: set[int], k: int = K) -> float:
    for position, pid in enumerate(ranked[:k], start=1):
        if pid in relevant:
            return 1 / position
    return 0.0


def ndcg_at(ranked: list[int], relevant: set[int], k: int = K) -> float:
    dcg = sum(1 / math.log2(i + 1) for i, pid in enumerate(ranked[:k], start=1) if pid in relevant)
    ideal = sum(1 / math.log2(i + 1) for i in range(1, min(len(relevant), k) + 1))
    return dcg / ideal if ideal else 0.0


def percentile(values: list[float], p: float) -> float:
    ordered = sorted(values)
    return ordered[max(0, math.ceil(p * len(ordered)) - 1)]


def _rank_timed(db, q: str, mode: str) -> tuple[list[int], float]:
    start = time.perf_counter()
    qvec = None if mode == "lexical" else embed([q], "query")[0]
    ranked = service.rank(db, q, mode, qvec)
    return ranked, (time.perf_counter() - start) * 1000


def evaluate(db, cases: list[dict]) -> dict:
    ids = dict(db.execute(select(Product.slug, Product.id)).all())
    missing = {slug for case in cases for slug in case["relevant"]} - ids.keys()
    if missing:
        raise SystemExit(f"unknown slugs in the query set: {sorted(missing)}")

    _rank_timed(db, "warm up", "hybrid")  

    results: dict = defaultdict(lambda: defaultdict(list))  
    for case in cases:
        q = service.normalize_query(case["q"])
        relevant = {ids[slug] for slug in case["relevant"]}
        for mode in MODES:
            ranked, ms = _rank_timed(db, q, mode)
            for group in ("all", case["kind"]):
                metrics = results[(group, mode)]
                metrics["p5"].append(precision_at(ranked, relevant))
                metrics["mrr"].append(mrr_at(ranked, relevant))
                metrics["ndcg"].append(ndcg_at(ranked, relevant))
                metrics["ms"].append(ms)
    return results


def to_markdown(results: dict) -> str:
    lines = [
        "| Queries | Mode | P@5 | MRR@10 | nDCG@10 | p50, ms | p95, ms |",
        "|---|---|---|---|---|---|---|",
    ]
    order = sorted(results, key=lambda key: (key[0] != "all", key[0], MODES.index(key[1])))
    for group, mode in order:
        m = results[(group, mode)]
        lines.append(
            f"| {group} ({len(m['p5'])}) | {mode} | {mean(m['p5']):.2f} | {mean(m['mrr']):.2f} "
            f"| {mean(m['ndcg']):.2f} | {percentile(m['ms'], 0.5):.0f} | {percentile(m['ms'], 0.95):.0f} |"
        )
    return "\n".join(lines)


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_QUERIES
    cases = json.loads(path.read_text(encoding="utf-8"))
    db = get_session()
    try:
        results = evaluate(db, cases)
    except EmbedderUnavailable as exc:
        raise SystemExit(f"embedder unavailable, evaluation needs it: {exc}")
    finally:
        db.rollback()  
        db.close()
    print(to_markdown(results))


if __name__ == "__main__":
    main()