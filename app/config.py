"""Cấu hình service theo biến môi trường."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Cấu hình runtime; API key bắt buộc để service fail fast."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    port: int = 8000
    agent_api_key: str
    redis_url: str = "redis://localhost:6379/0"
    rate_limit_per_minute: int = 10
    monthly_budget_usd: float = 10.0
    log_level: str = "INFO"
    llm_provider: Literal["mock", "openai"] = "mock"
    openai_api_key: SecretStr | None = None
    openai_model: str = "gpt-6-luna"
    openai_max_output_tokens: int = Field(default=512, ge=1, le=128_000)
    openai_input_usd_per_million: float = Field(default=0.10, ge=0)
    openai_cached_input_usd_per_million: float = Field(default=0.01, ge=0)
    openai_cache_write_usd_per_million: float = Field(default=0.125, ge=0)
    openai_output_usd_per_million: float = Field(default=0.50, ge=0)

    @field_validator("agent_api_key")
    @classmethod
    def validate_agent_api_key(cls, value: str) -> str:
        """Từ chối API key rỗng."""
        value = value.strip()
        if not value:
            raise ValueError("AGENT_API_KEY must not be blank")
        return value

    @field_validator("openai_api_key", mode="before")
    @classmethod
    def normalize_openai_api_key(cls, value):
        """Coi biến OpenAI để trống như chưa cấu hình."""
        if value is None or (isinstance(value, str) and not value.strip()):
            return None
        return value

    @field_validator("openai_model")
    @classmethod
    def validate_openai_model(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("OPENAI_MODEL must not be blank")
        return value

    @model_validator(mode="after")
    def validate_openai_configuration(self):
        """Chỉ bắt buộc OpenAI key khi người dùng bật provider này."""
        if self.llm_provider == "openai" and self.openai_api_key is None:
            raise ValueError(
                "OPENAI_API_KEY is required when LLM_PROVIDER=openai"
            )
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Đọc và cache cấu hình runtime."""
    return Settings()
