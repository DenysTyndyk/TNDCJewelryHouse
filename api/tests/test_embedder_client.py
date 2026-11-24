import httpx
import pytest

from app.services.search import embedder_client
from app.services.search.embedder_client import EmbedderUnavailable, embed


def test_embed_raises_when_service_down(monkeypatch):
    def fake_post(*args, **kwargs):
        raise httpx.ConnectError("connection refused")

    monkeypatch.setattr(embedder_client.httpx, "post", fake_post)
    with pytest.raises(EmbedderUnavailable):
        embed(["кільце"], "query")


def test_embed_returns_vectors(monkeypatch):
    def fake_post(url, json, timeout):
        return httpx.Response(200, json={"vectors": [[0.1] * 384]}, request=httpx.Request("POST", url))

    monkeypatch.setattr(embedder_client.httpx, "post", fake_post)
    assert len(embed(["кільце"], "query")[0]) == 384