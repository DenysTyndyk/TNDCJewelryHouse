from app.core.config import settings
from tests.test_recommendation_repository import _product, _variant
from tests.test_search_repository import DIM, _embedding, _unit

GUEST = "similar-vector-guest-0001"


def _mix(a: int, b: int, weight_b: float) -> list[float]:
    vec = [0.0] * DIM
    vec[a], vec[b] = 1.0, weight_b
    return vec


def _with_embedding(db, slug, sku, vec):
    product = _product(db, slug)
    _variant(db, product, sku, "1000.00", 5)
    _embedding(db, product, "uk", vec)
    return product


def _similar(client, product_id):
    resp = client.get(f"/recommendations/similar/{product_id}", headers={"X-Cart-Session": GUEST})
    assert resp.status_code == 200
    return resp.json()


def test_vector_source_puts_nearest_first(client, db_session, monkeypatch):
    monkeypatch.setattr(settings, "similar_source", "vector")
    target = _with_embedding(db_session, "simvec-target", "SIMVEC-1", _unit(7))
    near = _with_embedding(db_session, "simvec-near", "SIMVEC-2", _mix(7, 8, 0.1))
    _with_embedding(db_session, "simvec-far", "SIMVEC-3", _mix(7, 8, 3.0))
    db_session.flush()

    body = _similar(client, target.id)
    assert body["algorithm"] == "vector"
    assert body["items"][0]["id"] == near.id
    assert target.id not in [i["id"] for i in body["items"]]


def test_vector_without_embeddings_falls_back_to_content(client, db_session, monkeypatch):
    monkeypatch.setattr(settings, "similar_source", "vector")
    target = _product(db_session, "simvec-noemb")
    _variant(db_session, target, "SIMVEC-4", "1000.00", 5)
    db_session.flush()
    assert _similar(client, target.id)["algorithm"] == "content"


def test_default_source_is_content(client, db_session):
    target = _product(db_session, "simvec-default")
    _variant(db_session, target, "SIMVEC-5", "1000.00", 5)
    db_session.flush()
    assert _similar(client, target.id)["algorithm"] == "content"