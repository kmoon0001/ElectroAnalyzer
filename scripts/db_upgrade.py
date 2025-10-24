#!/usr/bin/env python3
"""Run Alembic upgrade to head if Alembic is available.

Safe to run multiple times; logs and exits non-fatal on failure when used in dev.
"""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    try:
        from alembic.config import CommandLine
    except Exception:
        print("Alembic not installed; skipping db upgrade.")
        return 0

    cli = CommandLine(prog="alembic")
    # Ensure we run from project root with alembic.ini present
    root = Path(__file__).resolve().parents[1]
    with (root / "alembic.ini").open("r", encoding="utf-8"):
        pass
    argv = ["upgrade", "head"]
    try:
        cli.main(argv=argv)
        return 0
    except SystemExit as e:
        return int(e.code or 0)


if __name__ == "__main__":
    sys.exit(main())

