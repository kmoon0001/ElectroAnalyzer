#!/usr/bin/env python3
"""Lightweight smoke test: import the app and hit health endpoints.

Uses FastAPI's TestClient to avoid starting an external server.
"""

from __future__ import annotations

import os
from typing import Any

from fastapi.testclient import TestClient


def main() -> int:
    os.environ.setdefault("USE_AI_MOCKS", "true")
    os.environ.setdefault("SECRET_KEY", "test-secret")
    os.environ.setdefault("DISABLE_EXTERNAL_CHECKS", "true")

    from src.api.main import app

    with TestClient(app) as client:
        r = client.get("/health/")
        assert r.status_code in (200, 503), f"unexpected status: {r.status_code}"
        r2 = client.get("/health/system")
        assert r2.status_code in (200, 503), f"unexpected status: {r2.status_code}"
        # Docs route is present by default in dev
        rd = client.get("/docs")
        assert rd.status_code in (200, 404), f"unexpected docs: {rd.status_code}"
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

