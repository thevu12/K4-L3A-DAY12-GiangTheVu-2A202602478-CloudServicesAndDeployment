"""Chọn LLM backend và chuẩn hóa kết quả cho endpoint ``/ask``."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

import openai
from openai import OpenAI

from utils.mock_llm import ask_llm as _ask_mock_llm

from .config import get_settings

SYSTEM_INSTRUCTIONS = (
    "Bạn là trợ lý kỹ thuật. Hãy trả lời đúng trọng tâm, rõ ràng và bằng "
    "ngôn ngữ mà người dùng đang sử dụng. Không bịa thông tin khi không chắc chắn."
)


class LLMProviderError(RuntimeError):
    """Lỗi provider đã được rút gọn để không làm lộ dữ liệu nhạy cảm."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


@lru_cache(maxsize=1)
def _get_openai_client() -> OpenAI:
    settings = get_settings()
    if settings.openai_api_key is None:
        raise LLMProviderError("configuration")
    return OpenAI(
        api_key=settings.openai_api_key.get_secret_value(),
        timeout=25.0,
        max_retries=0,
    )


def _messages(question: str, history: list[dict] | None) -> list[dict[str, str]]:
    messages: list[dict[str, str]] = []
    for turn in history or []:
        role = turn.get("role")
        content = turn.get("content")
        if role in {"user", "assistant"} and isinstance(content, str) and content:
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": question})
    return messages


def _provider_error_code(error: openai.OpenAIError) -> str:
    if isinstance(error, openai.AuthenticationError):
        return "authentication"
    if isinstance(error, openai.RateLimitError):
        return "rate_limit"
    if isinstance(error, openai.APITimeoutError):
        return "timeout"
    if isinstance(error, openai.APIConnectionError):
        return "connection"
    return "api_error"


def _usage_value(value: Any) -> int:
    return max(int(value or 0), 0)


def _openai_cost(response, settings) -> tuple[int, int, float]:
    usage = response.usage
    if usage is None:
        raise LLMProviderError("missing_usage")

    tokens_in = _usage_value(usage.input_tokens)
    tokens_out = _usage_value(usage.output_tokens)
    details = getattr(usage, "input_tokens_details", None)
    cached_tokens = _usage_value(getattr(details, "cached_tokens", 0))
    cache_write_tokens = _usage_value(
        getattr(details, "cache_write_tokens", 0)
    )
    regular_tokens = max(tokens_in - cached_tokens - cache_write_tokens, 0)

    cost = (
        regular_tokens * settings.openai_input_usd_per_million
        + cached_tokens * settings.openai_cached_input_usd_per_million
        + cache_write_tokens * settings.openai_cache_write_usd_per_million
        + tokens_out * settings.openai_output_usd_per_million
    ) / 1_000_000
    return tokens_in, tokens_out, round(cost, 8)


def _ask_openai(question: str, history: list[dict] | None) -> dict:
    settings = get_settings()
    try:
        response = _get_openai_client().responses.create(
            model=settings.openai_model,
            instructions=SYSTEM_INSTRUCTIONS,
            input=_messages(question, history),
            max_output_tokens=settings.openai_max_output_tokens,
            reasoning={"effort": "none"},
            store=False,
        )
    except openai.OpenAIError as error:
        raise LLMProviderError(_provider_error_code(error)) from None

    answer = response.output_text.strip()
    if not answer:
        raise LLMProviderError("empty_response")
    tokens_in, tokens_out, cost = _openai_cost(response, settings)
    return {
        "answer": answer,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "cost_usd": cost,
    }


def ask_llm(question: str, history: list[dict] | None = None) -> dict:
    """Gọi provider đã chọn nhưng giữ nguyên contract LLM hiện tại."""
    if get_settings().llm_provider == "openai":
        return _ask_openai(question, history)
    return _ask_mock_llm(question, history)
