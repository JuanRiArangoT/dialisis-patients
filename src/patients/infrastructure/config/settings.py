import json
import os
from functools import lru_cache
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    auth0_domain: str
    auth0_api_audience: str
    users_service_url: str
    roles_service_url: str
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> list[str]:
        if isinstance(v, str):
            clean = v.strip()
            if clean.startswith("[") and clean.endswith("]"):
                try:
                    parsed = json.loads(clean)
                    if isinstance(parsed, list):
                        return [
                            str(item).strip() for item in parsed if str(item).strip()
                        ]
                except (json.JSONDecodeError, TypeError, ValueError):
                    return [
                        origin.strip().strip("'\"")
                        for origin in clean.strip("[]").split(",")
                        if origin.strip().strip("'\"")
                    ]
            return [origin.strip() for origin in clean.split(",") if origin.strip()]
        if isinstance(v, (list, tuple)):
            return [str(origin).strip() for origin in v if str(origin).strip()]
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
