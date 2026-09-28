"""Kiểm tra giao diện web và các header bảo mật."""

from __future__ import annotations

import re


def test_home_returns_html(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "Cloud Agent" in response.text


def test_home_uses_matching_csp_nonce(client):
    response = client.get("/")
    policy = response.headers["content-security-policy"]
    match = re.search(r"script-src 'nonce-([^']+)'", policy)

    assert match, policy
    nonce = match.group(1)
    assert f'script nonce="{nonce}"' in response.text
    assert f'style nonce="{nonce}"' in response.text
    assert "'unsafe-inline'" not in policy


def test_home_does_not_cache_or_expose_test_key(client, api_key):
    response = client.get("/")

    assert response.headers["cache-control"] == "no-store"
    assert response.headers["x-frame-options"] == "DENY"
    assert api_key not in response.text


def test_form_matches_ask_contract(client):
    body = client.get("/").text

    assert 'type="password"' in body
    assert 'name="question"' in body
    assert 'maxlength="2000"' in body
    assert 'fetch("/ask"' in body
    assert "localStorage" not in body
    assert "sessionStorage" not in body
    assert "innerHTML" not in body


def test_form_handles_timeout_and_invalid_responses(client):
    body = client.get("/").text

    assert "new AbortController()" in body
    assert "requestTimeoutMs = 30000" in body
    assert 'typeof payload.answer !== "string"' in body
    assert 'error.name === "AbortError"' in body
    assert "Number.isFinite(tokensIn)" in body


def test_api_key_privacy_note_is_accessible(client):
    body = client.get("/").text

    assert 'aria-describedby="api-key-note"' in body
    assert 'id="api-key-note"' in body


def test_home_does_not_depend_on_redis(client_factory):
    class UnavailableStore:
        def ping(self):
            return False

    response = client_factory(store=UnavailableStore()).get("/")
    assert response.status_code == 200
