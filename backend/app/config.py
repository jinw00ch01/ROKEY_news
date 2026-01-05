from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    gemini_api_key: str | None = None
    newsdata_api_key: str | None = None
    database_url: str = "sqlite:///./local.db"
    allowed_origins: list[str] | str = ["*"]
    rate_limit_per_min: int = 60

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def _coerce_origins(cls, v: str | list[str]) -> list[str]:
        if v is None:
            return ["*"]
        if isinstance(v, list):
            return v
        # "http://a,https://b" 형태를 리스트로 변환
        return [part.strip() for part in v.split(",") if part.strip()]

    @property
    def allowed_origins_list(self) -> List[str]:
        return self.allowed_origins  # validator에서 이미 리스트로 정규화됨


@lru_cache
def get_settings() -> Settings:
    return Settings()
