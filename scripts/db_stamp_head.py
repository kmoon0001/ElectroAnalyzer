#!/usr/bin/env python3
"""Stamp the database to Alembic head revision without running Alembic.

This is a safe, idempotent way to align an existing SQLite DB with the
initial migration revision when Alembic isn't installed in the environment.
"""

from __future__ import annotations

import asyncio
from sqlalchemy import text
from src.database.database import engine


async def main() -> int:
    revision = "0001_initial"
    ddl_create = (
        "CREATE TABLE IF NOT EXISTS alembic_version ("
        "version_num VARCHAR(32) NOT NULL)"
    )
    async with engine.begin() as conn:
        await conn.execute(text(ddl_create))
        # clear existing rows to enforce single-row semantics
        await conn.execute(text("DELETE FROM alembic_version"))
        await conn.execute(
            text("INSERT INTO alembic_version (version_num) VALUES (:v)"),
            {"v": revision},
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))

