from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Default to SQLite so the app runs without Docker. Switch to Postgres via .env.
    database_url: str = "sqlite:///./marketlens.db"
    app_name: str = "MarketLens"

    # Mistral (free-tier friendly) for AI narrative polish
    mistral_api_key: str | None = None
    mistral_model: str = "mistral-small-latest"
    mistral_base_url: str = "https://api.mistral.ai/v1"


@lru_cache
def get_settings() -> Settings:
    return Settings()
