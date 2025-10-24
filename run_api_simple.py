#!/usr/bin/env python3
"""Simple API startup script that bypasses complex initialization."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

async def main():
    print("Starting API server...")

    # Set AI mocks to true
    import os
    os.environ['USE_AI_MOCKS'] = 'true'

    # Import app
    from src.api.main import app

    print("App imported successfully!")

    # Start uvicorn
    import uvicorn

    config = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=8001,
        log_level="info",
        access_log=True,
    )
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
