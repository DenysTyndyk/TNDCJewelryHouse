from collections import Counter

def apply_rules(
    ranked: list[tuple[int,float]],
    *,
    available: set[int],
    exclude: set[int],
    category: dict[int,int],
    limit: int,
    max_per_category: int,
    ) -> list[tuple[int,float]]:
    result: list[tuple[int,float]] = []
    per_category: Counter[int] = Counter()
    for pid, s in ranked: 
        if pid not in available or pid in  exclude:
            continue
        cat = category[pid]
        if per_category[cat] >= max_per_category:
            continue
        per_category[cat] += 1
        result.append((pid,s))
        if len(result) == limit:
            break
    return result
