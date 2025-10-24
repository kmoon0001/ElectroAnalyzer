"""Database package public API with lazy imports to avoid heavy side-effects.

Exposes:
- crud, models, schemas (lazy-loaded)
- Base, engine, get_async_db, get_db, init_db, AsyncSessionLocal
"""

from __future__ import annotations

import importlib
from typing import Any

from .database import AsyncSessionLocal, Base, engine, get_async_db, get_db, init_db

__all__ = [
    "crud",
    "models",
    "schemas",
    "Base",
    "engine",
    "get_async_db",
    "get_db",
    "init_db",
    "AsyncSessionLocal",
]


def __getattr__(name: str) -> Any:  # PEP 562 lazy imports
    if name in {"crud", "models", "schemas"}:
        return importlib.import_module(f".{name}", __name__)
    raise AttributeError(name)
