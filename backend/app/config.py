import json
from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    gemini_api_key: str | None = None
    database_url: str = "sqlite:///./local.db"
    allowed_origins: list[str] | str = ["*"]  # Render에서 단일 문자열도 허용
    rate_limit_per_min: int = 60
    rss_sources: list[dict[str, str]] | str | dict | None = None

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def _coerce_origins(cls, v: str | list[str]) -> list[str]:
        if v is None:
            return ["*"]
        if isinstance(v, list):
            return v
        # "http://a,https://b" 형태를 리스트로 변환
        return [part.strip() for part in v.split(",") if part.strip()]

    @field_validator("rss_sources", mode="before")
    @classmethod
    def _coerce_rss(cls, v):
        if v is None:
            return None
        if isinstance(v, list):
            return v
        if isinstance(v, dict):
            return [v]
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, dict):
                    return [parsed]
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                # fallback: single URL string
                return [{"name": v, "url": v}]
        raise ValueError("rss_sources must be list/dict/json string")

    @property
    def allowed_origins_list(self) -> List[str]:
        return self.allowed_origins  # validator에서 이미 리스트로 정규화됨


@lru_cache
def get_settings() -> Settings:
    return Settings()

