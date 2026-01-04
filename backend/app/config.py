from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    gemini_api_key: str | None = None
    database_url: str = "sqlite:///./local.db"
    allowed_origins: list[str] = ["*"]
    rate_limit_per_min: int = 60
    rss_sources: list[dict[str, str]] | str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()

