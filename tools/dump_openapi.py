#!/usr/bin/env python3
"""Dump FastAPI OpenAPI schema and a quick summary to files.

Writes:
- openapi.json
- openapi_summary.txt
"""

from __future__ import annotations

import json
from pathlib import Path
from collections import defaultdict


def main() -> None:
    # Import app lazily after setting path via cwd
    from src.api.main import app

    data = app.openapi()
    Path("openapi.json").write_text(json.dumps(data, indent=2), encoding="utf-8")

    paths: dict[str, dict] = data.get("paths", {})  # type: ignore[assignment]
    lines: list[str] = []
    info = data.get("info", {})
    lines.append(f"title: {info.get('title')}")
    lines.append(f"version: {info.get('version')}")
    lines.append(f"total_paths: {len(paths)}")

    # tags
    tag_set: set[str] = set()
    for p, methods in paths.items():
        for m, op in methods.items():
            if not isinstance(op, dict):
                continue
            for t in (op.get("tags") or []):
                tag_set.add(str(t))
    lines.append("tags: " + ", ".join(sorted(tag_set)))

    # presence of key endpoints
    key_eps = [
        "/health",
        "/health/",
        "/health/system",
        "/metrics",
        "/auth/token",
        "/analysis/analyze",
    ]
    for ep in key_eps:
        lines.append(f"exists {ep}: {'yes' if ep in paths else 'no'}")

    lines.append("")
    lines.append("first_paths:")
    for i, (p, methods) in enumerate(sorted(paths.items())):
        if i >= 80:
            break
        meths = [k for k in methods.keys() if k in {"get", "post", "put", "delete", "patch"}]
        lines.append(f"- {p} [{' '.join(meths)}]")

    # security schemes
    components = data.get("components", {})
    sec_schemes = list((components.get("securitySchemes") or {}).keys())
    lines.append("")
    lines.append("security_schemes: " + ", ".join(sec_schemes))

    Path("openapi_summary.txt").write_text("\n".join(lines), encoding="utf-8")
    print("Wrote openapi.json and openapi_summary.txt")


if __name__ == "__main__":
    main()

