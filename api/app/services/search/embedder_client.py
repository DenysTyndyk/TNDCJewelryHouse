from typing import Literal

import httpx

from app.core.config import settings


class EmbedderUnavailable(Exception):
    """Embedder is down, timed out or returned an invalid response; callers fall back to lexical search."""

def embed(texts: list[str], kind: Literal["query","passage"],timeout:float = 2.0) -> list[list[float]]:
    if not texts:
        return []
    try:
        response = httpx.post(
            f"{settings.embedder_url}/embed",
            json={"texts": texts,"kind":kind},
            timeout=timeout,
        )
        response.raise_for_status()
        vectors = response.json()["vectors"]
    except(httpx.HTTPError,ValueError,KeyError) as exc:
        raise EmbedderUnavailable(str(exc)) from exc
    if len(vectors) != len(texts):
        raise EmbedderUnavailable(f"expected {len(texts)} vectors, got {len(vectors)}")
    return vectors
