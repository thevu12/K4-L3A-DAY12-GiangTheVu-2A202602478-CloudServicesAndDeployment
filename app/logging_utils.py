"""Ghi log JSON một dòng cho cloud log collectors."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone


def utc_now_iso() -> str:
    """Trả về thời gian UTC theo ISO-8601."""
    return datetime.now(timezone.utc).isoformat()


def log_event(event: str, level: str = "info", **fields) -> str:
    """In và trả về một JSON event trên đúng một dòng stdout."""
    payload = {
        "event": event,
        "level": level.lower(),
        "timestamp": utc_now_iso(),
    }
    payload.update(fields)
    encoded = json.dumps(payload, ensure_ascii=False)
    print(encoded, file=sys.stdout)
    return encoded
