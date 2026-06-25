"""Tiny disk cache with a graceful-degradation fallback.

The goal is production resilience for a live demo: a successful response is
written to ``cache/<key>.json``. If the upstream pharma APIs are slow or down on
a later request, we serve the last good payload (flagged ``degraded``) rather
than showing an empty screen. TTL keeps fresh data flowing when the APIs are up.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from typing import Optional

CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "cache")
TTL_SECONDS = 60 * 60 * 12  # 12h


def _path(key: str) -> str:
    digest = hashlib.sha1(key.lower().strip().encode()).hexdigest()[:16]
    return os.path.join(CACHE_DIR, f"{digest}.json")


def read(key: str, allow_stale: bool = False) -> Optional[dict]:
    """Return cached payload. Fresh within TTL, or any age if allow_stale."""
    p = _path(key)
    if not os.path.exists(p):
        return None
    try:
        with open(p, "r", encoding="utf-8") as f:
            entry = json.load(f)
        age = time.time() - entry.get("_ts", 0)
        if age <= TTL_SECONDS or allow_stale:
            return entry.get("data")
    except Exception:
        return None
    return None


def write(key: str, data: dict) -> None:
    os.makedirs(CACHE_DIR, exist_ok=True)
    try:
        with open(_path(key), "w", encoding="utf-8") as f:
            json.dump({"_ts": time.time(), "data": data}, f)
    except Exception:
        pass
