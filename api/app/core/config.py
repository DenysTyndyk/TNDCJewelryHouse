from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

MEDIA_DIR = Path(__file__).resolve().parents[2] / "media"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")

    database_url: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    password_pepper: str = Field(min_length=32)
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30
    refresh_reuse_grace_seconds: int = 5
    max_failed_attempts: int = 5
    lockout_duration: int = 15 # in minutes
    refresh_token_length: int = 64
    email_verification_token_expire_hours: int = 24
    password_reset_token_expire_minutes: int = 30
    frontend_base_url: str = "http://localhost:5173"
    media_base_url: str = "http://localhost:8000/media"
    cors_origins: list[str] = ["http://localhost:5173"]
    app_env: Literal["dev", "prod"] = "prod"
    pending_order_ttl_minutes: int = 30
    refresh_cookie_samesite: Literal["lax", "strict", "none"] = "lax"
    seed_admin_password: str | None = Field(default=None, min_length=12)
    event_retention_days: int = Field(default=365, ge=1)
    # Recommendations (M6). Hybrid score = a·behavior + b·content + c·popularity + d·novelty.
    # Components are normalised to [0, 1] first, so only the ratio between weights matters.
    reco_weight_behavior: float = Field(default=0.4, ge=0)
    reco_weight_content: float = Field(default=0.3, ge=0)
    reco_weight_popularity: float = Field(default=0.2, ge=0)
    reco_weight_novelty: float = Field(default=0.1, ge=0)
    # Time decay per day: weight·exp(−λ·days). λ=0.1 → half-life ≈ 7 days.
    reco_decay_lambda: float = Field(default=0.1, ge=0)
    # Older events weigh < exp(−λ·90) ≈ 0.0001, so they are not loaded at all.
    reco_history_days: int = Field(default=90, ge=1)
    reco_popularity_short_days: int = Field(default=7, ge=1)
    reco_popularity_long_days: int = Field(default=30, ge=1)
    reco_limit: int = Field(default=12, ge=1, le=50)
    # Diversity rule: at most N items from one category in a single list.
    reco_max_per_category: int = Field(default=4, ge=1)
    # Search (M7): embedding service; compose overrides this with http://embedder:8001.
    embedder_url: str = "http://localhost:8001"
    embedding_model: str = "intfloat/multilingual-e5-small"
    embedding_version: int = Field(default=1, ge=1)
    semantic_search_enabled: bool = True
    similar_source: Literal["cbf", "vector"] = "cbf"
    search_rrf_k: int = Field(default=60, ge=1)

settings = Settings()
