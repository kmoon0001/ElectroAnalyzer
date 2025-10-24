#!/usr/bin/env python3
"""Safe repo cleanup utility.

Removes temp and cache artifacts that are safe to delete and do not force
re-downloads of heavy assets. Preserves virtual envs, node_modules, and models.

Usage examples:
  - python tools/cleanup_safe.py                 # full safe cleanup
  - python tools/cleanup_safe.py --logs --temp   # only logs + temp

What it removes (by default):
  - __pycache__/ directories and *.pyc/*.pyo (outside venv/node_modules)
  - .pytest_cache/, .mypy_cache/, .ruff_cache/ (repo-level)
  - Contents of .cache/ (app runtime cache)
  - Contents of temp/ (temporary uploads)
  - Contents of logs/ (keeps folder)

What it never removes:
  - venv*/ directories (Python environments)
  - frontend/*/node_modules/ (npm installs)
  - models/ (local model files)
"""

from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

# Exclusion roots we always preserve
EXCLUDE_PREFIXES = [
    ROOT / "venv_fresh",
    ROOT / "venv",
    ROOT / "frontend" / "electron-react-app" / "node_modules",
    ROOT / "models",
]


def is_excluded(path: Path) -> bool:
    try:
        p = path.resolve()
    except Exception:
        p = path
    for ex in EXCLUDE_PREFIXES:
        try:
            if str(p).startswith(str(ex.resolve())):
                return True
        except Exception:
            if str(p).startswith(str(ex)):
                return True
    return False


def rm_tree(p: Path) -> bool:
    if not p.exists():
        return True
    if is_excluded(p):
        return False
    try:
        shutil.rmtree(p)
        return True
    except Exception:
        return False


def rm_glob(root: Path, patterns: list[str]) -> tuple[int, int]:
    removed, failed = 0, 0
    for pat in patterns:
        for item in root.rglob(pat):
            if is_excluded(item):
                continue
            try:
                item.unlink()
                removed += 1
            except IsADirectoryError:
                if rm_tree(item):
                    removed += 1
                else:
                    failed += 1
            except Exception:
                failed += 1
    return removed, failed


def clear_dir_contents(dir_path: Path) -> tuple[int, int]:
    if not dir_path.exists() or not dir_path.is_dir():
        return 0, 0
    removed, failed = 0, 0
    for child in dir_path.iterdir():
        if is_excluded(child):
            continue
        try:
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
            removed += 1
        except Exception:
            failed += 1
    return removed, failed


def main() -> int:
    ap = argparse.ArgumentParser(description="Safe cleanup (no heavy re-downloads)")
    ap.add_argument("--logs", action="store_true", help="clear logs/")
    ap.add_argument("--temp", action="store_true", help="clear temp/")
    ap.add_argument("--cache", action="store_true", help="clear .cache/")
    ap.add_argument("--pyc", action="store_true", help="remove __pycache__ and *.pyc")
    ap.add_argument("--tool-caches", action="store_true", help="remove .pytest_cache/.mypy_cache/.ruff_cache")
    ap.add_argument("--all", action="store_true", help="run all safe cleanups (default)")
    args = ap.parse_args()

    do_all = args.all or not any(
        [args.logs, args.temp, args.cache, args.pyc, args.tool_caches]
    )

    total_removed = 0
    total_failed = 0

    # 1) Python bytecode caches
    if do_all or args.pyc:
        removed, failed = rm_glob(ROOT, ["__pycache__", "*.pyc", "*.pyo"])
        total_removed += removed
        total_failed += failed

    # 2) Tool caches at repo root
    if do_all or args.tool_caches:
        for name in (".pytest_cache", ".mypy_cache", ".ruff_cache"):
            d = ROOT / name
            if d.exists() and d.is_dir() and not is_excluded(d):
                if rm_tree(d):
                    total_removed += 1
                else:
                    total_failed += 1

    # 3) App runtime cache
    if do_all or args.cache:
        removed, failed = clear_dir_contents(ROOT / ".cache")
        total_removed += removed
        total_failed += failed

    # 4) Temp uploads
    if do_all or args.temp:
        removed, failed = clear_dir_contents(ROOT / "temp")
        total_removed += removed
        total_failed += failed

    # 5) Logs
    if do_all or args.logs:
        removed, failed = clear_dir_contents(ROOT / "logs")
        total_removed += removed
        total_failed += failed

    print(f"removed={total_removed} failed={total_failed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

