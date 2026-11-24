from types import SimpleNamespace

import pytest

from app.core.config import settings
from app.models.enums import SearchType
from app.models.telemetry import SearchQuery
from app.repositories import catalog_repository, search_repository
from app.schemas.catalog import ProductFilter
from app.services.search import service
from app.services.search.embedder_client import EmbedderUnavailable

VEC = [0.0] * 384


def test_rrf_sums_reciprocal_ranks():
    # 2: 1/61 + 1/62 beats 1: 1/61 only
    assert service.rrf([[2, 1], [3, 2]], k=60)[0] == 2


def test_rrf_tie_broken_by_id():
    assert service.rrf([[5], [4]], k=60) == [4, 5]


def test_rrf_empty():
    assert service.rrf([[], []]) == []


@pytest.fixture
def fake_backends(monkeypatch):
    monkeypatch.setattr(search_repository, "lexical", lambda db, q, limit=100: [1, 2, 3])
    monkeypatch.setattr(search_repository, "semantic", lambda db, qvec, limit=100: [3, 4])
    monkeypatch.setattr(search_repository, "cached_query_embedding", lambda db, q: None)
    # SQL filters drop product 2.
    monkeypatch.setattr(
        catalog_repository, "list_products",
        lambda db, f, cur, ids=None: ([SimpleNamespace(id=i) for i in ids if i != 2], None),
    )


def _run(db, mode="hybrid", tracking=True):
    return service.search(
        db, "  Каблучка ", mode, ProductFilter(limit=10), "uk",
        user_id=None, session_token="s" * 32, tracking=tracking,
    )


def test_hybrid_ranks_and_filters(db_session, fake_backends, monkeypatch):
    monkeypatch.setattr(service, "embed", lambda texts, kind: [VEC])
    result = _run(db_session)
    assert result.mode_used == "hybrid"
    assert result.ids[0] == 3  # present in both rankings
    assert 2 not in result.ids
    assert result.total == 3


def test_embedder_down_falls_back_to_lexical(db_session, fake_backends, monkeypatch):
    def boom(texts, kind):
        raise EmbedderUnavailable("down")
    monkeypatch.setattr(service, "embed", boom)
    assert _run(db_session).mode_used == "lexical"


def test_flag_off_skips_embedder(db_session, fake_backends, monkeypatch):
    monkeypatch.setattr(settings, "semantic_search_enabled", False)
    monkeypatch.setattr(service, "embed", lambda *a: pytest.fail("embedder must not be called"))
    assert _run(db_session, mode="semantic").mode_used == "lexical"


def test_log_without_consent_has_no_identity(db_session, fake_backends, monkeypatch):
    monkeypatch.setattr(service, "embed", lambda texts, kind: [VEC])
    _run(db_session, tracking=False)
    row = db_session.query(SearchQuery).order_by(SearchQuery.id.desc()).first()
    assert row.query_text == "каблучка"
    assert row.session_token is None and row.user_id is None
    assert row.query_embedding is not None  # cache kept without consent
    assert row.search_type == SearchType.Hybrid