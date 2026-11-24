"""Embedding service: intfloat/multilingual-e5-small behind a small HTTP API."""
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer

MODEL_NAME = "intfloat/multilingual-e5-small"
model: SentenceTransformer | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load once at startup; uvicorn does not accept requests until this finishes.
    global model
    model = SentenceTransformer(MODEL_NAME, device="cpu")
    yield


app = FastAPI(title="TNDC embedder", lifespan=lifespan)


class EmbedIn(BaseModel):
    texts: list[str] = Field(min_length=1, max_length=64)
    kind: Literal["query", "passage"]


class EmbedOut(BaseModel):
    vectors: list[list[float]]


@app.post("/embed", response_model=EmbedOut)
def embed(body: EmbedIn) -> EmbedOut:
    # e5 was trained with these prefixes; without them retrieval quality drops.
    texts = [f"{body.kind}: {t}" for t in body.texts]
    vectors = model.encode(texts, normalize_embeddings=True)
    return EmbedOut(vectors=vectors.tolist())


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "model": MODEL_NAME}
