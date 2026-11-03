from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")

    database_url: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30
    refresh_reuse_grace_seconds: int = 5
    max_failed_attempts: int = 5
    lockout_duration: int = 15 # in minutes
    refresh_token_length: int = 64
    email_verification_token_expire_hours: int = 24
    password_reset_token_expire_minutes: int = 30
    frontend_base_url: str = "http://localhost:5173"
    cors_origins: list[str] = ["http://localhost:5173"]

settings = Settings()
