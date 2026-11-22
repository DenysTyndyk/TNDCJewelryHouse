import math

Vector = dict[str,float]

def _normalize(v: Vector):
    norm = math.sqrt(sum(x*x for x in v.values()))
    return {k: x/norm for k , x in v.items()} if norm else v

def build_vectors(features) -> dict[int, Vector]:
    prices = [float(f.price) for f in features]
    lo, hi = min(prices,default=0.0), max(prices,default=0.0)
    span = hi - lo
    vectors: dict[int,Vector] = {}
    for f in features:
        v: Vector = {f"cat:{f.category_id}": 1.0}
        for prefix , values in (
            ("metal", f.metals),
            ("color", f.colors),
            ("fineness", f.finenesses),
            ("gem", f.gemstones),
        ): 
            for value in values or ():
                v[f"{prefix}:{value}"] = 1.0
        if span:
            v["price"] = (float(f.price) - lo) / span
        vectors[f.id] = _normalize(v)
    return vectors

def cosine(a: Vector, b: Vector):
    if len(a) > len(b):
        a ,b = b, a
    return sum(x*b[k] for k,x in a.items() if k in b)

def similar(vectors, categories: dict[int, int], product_id: int, k: int):
    target = vectors.get(product_id)
    if target is None:
        return []
    cat = categories[product_id]
    scored = [(pid, cosine(target, v)) for pid, v in vectors.items() if pid != product_id]
    scored.sort(key=lambda p: (categories[p[0]] == cat, p[1]), reverse=True)
    return scored[:k]

def profile_vector(weighted: dict[int, float], vectors: dict[int, Vector]) -> Vector:
    profile: Vector = {}
    for pid, w in weighted.items():
        for key, x in vectors.get(pid, {}).items(): 
            profile[key] = profile.get(key, 0.0) + w * x
    return _normalize(profile)
