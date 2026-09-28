"""Kiểm tra dispatcher mock/OpenAI mà không gọi mạng thật."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from pydantic import ValidationError


def _openai_settings():
    return SimpleNamespace(
        llm_provider="openai",
        openai_model="gpt-6-luna",
        openai_max_output_tokens=512,
        openai_input_usd_per_million=0.10,
        openai_cached_input_usd_per_million=0.01,
        openai_cache_write_usd_per_million=0.125,
        openai_output_usd_per_million=0.50,
    )


def test_mock_la_mac_dinh_khi_chua_co_openai_key(monkeypatch):
    from app import llm
    from app.config import Settings

    settings = Settings(agent_api_key="local-key", _env_file=None)
    assert settings.llm_provider == "mock"
    assert settings.openai_api_key is None

    monkeypatch.setattr(llm, "get_settings", lambda: settings)
    result = llm.ask_llm("Redis là gì?")
    assert result["answer"]
    assert result["cost_usd"] > 0


def test_bat_openai_nhung_thieu_key_thi_fail_fast(monkeypatch):
    from app.config import Settings

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ValidationError):
        Settings(
            agent_api_key="local-key",
            llm_provider="openai",
            openai_api_key="",
            _env_file=None,
        )


def test_openai_gui_history_va_tra_usage_that(monkeypatch):
    from app import llm

    captured = {}
    usage = SimpleNamespace(
        input_tokens=100,
        output_tokens=20,
        input_tokens_details=SimpleNamespace(
            cached_tokens=40,
            cache_write_tokens=10,
        ),
    )
    response = SimpleNamespace(output_text="  Câu trả lời thật.  ", usage=usage)

    class FakeResponses:
        def create(self, **kwargs):
            captured.update(kwargs)
            return response

    fake_client = SimpleNamespace(responses=FakeResponses())
    monkeypatch.setattr(llm, "get_settings", _openai_settings)
    monkeypatch.setattr(llm, "_get_openai_client", lambda: fake_client)

    result = llm.ask_llm(
        "Câu tiếp theo",
        [
            {"role": "user", "content": "Câu trước"},
            {"role": "assistant", "content": "Trả lời trước"},
            {"role": "system", "content": "Không được chuyển tiếp"},
        ],
    )

    assert captured["input"] == [
        {"role": "user", "content": "Câu trước"},
        {"role": "assistant", "content": "Trả lời trước"},
        {"role": "user", "content": "Câu tiếp theo"},
    ]
    assert captured["model"] == "gpt-6-luna"
    assert captured["store"] is False
    assert captured["max_output_tokens"] == 512
    assert result == {
        "answer": "Câu trả lời thật.",
        "tokens_in": 100,
        "tokens_out": 20,
        "cost_usd": pytest.approx(0.00001665),
    }


def test_provider_error_tra_502_va_khong_luu_history(
    client, auth_headers, monkeypatch, capsys
):
    from app import main as main_module
    from app.llm import LLMProviderError

    def fail(_question, _history):
        raise LLMProviderError("authentication")

    monkeypatch.setattr(main_module, "ask_llm", fail)
    response = client.post(
        "/ask", json={"question": "sentinel-question"}, headers=auth_headers
    )

    assert response.status_code == 502
    assert response.json() == {"detail": "LLM provider unavailable"}
    output = capsys.readouterr().out
    assert "sentinel-question" not in output
    assert "authentication" in output
