"""Xác thực API key cho endpoint công khai ``/ask``."""

from __future__ import annotations

import secrets

from fastapi import Header, HTTPException, status

from .config import get_settings

ANONYMOUS_USER = "anonymous"


def verify_api_key(
    x_api_key: str | None = Header(default=None),
    x_user_id: str | None = Header(default=None),
) -> str:
    """Xác thực ``X-API-Key`` và trả về user ID.

    ``compare_digest`` không short-circuit theo nội dung, giúp giảm rò rỉ timing.
    """
    expected_key = get_settings().agent_api_key
    if x_api_key is None or not secrets.compare_digest(x_api_key, expected_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid or missing API key",
        )
    return x_user_id or ANONYMOUS_USER
