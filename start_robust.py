#!/usr/bin/env python3
"""
Robust Startup Script for Therapy Compliance Analyzer
Handles port conflicts and process management automatically
"""

import asyncio
import logging
import sys
import subprocess
import time
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.persistent_task_registry import persistent_task_registry
from src.core.enhanced_worker_manager import enhanced_worker_manager
from src.database import init_db
from src.core.vector_store import get_vector_store
from src.logging_config import configure_logging
from src.config import get_settings

import structlog

logger = structlog.get_logger(__name__)


from typing import Optional


def find_available_port(start_port: int, max_attempts: int = 10) -> Optional[int]:
    """Find an available port starting from start_port."""
    import socket

    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                if result != 0:  # Port is available
                    return port
        except Exception:
            continue
    return None


def kill_process_on_port(port: int) -> bool:
    """Kill any process using the specified port."""
    try:
        # Find process using the port
        result = subprocess.run(
            f'netstat -ano | findstr ":{port}"',
            shell=True,
            capture_output=True,
            text=True
        )

        if result.stdout:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        try:
                            subprocess.run(f'taskkill /PID {pid} /F', shell=True, check=True)
                            logger.info(f"Killed process {pid} on port {port}")
                            time.sleep(1)  # Wait for port to be released
                            return True
                        except subprocess.CalledProcessError:
                            continue
        return False
    except Exception as e:
        logger.error(f"Failed to kill process on port {port}: {e}")
        return False


async def start_api_server(port: int = 8001) -> tuple[subprocess.Popen, int]:
    """Start the API server on the specified port."""
    # Optionally kill any existing process on the port (opt-in only)
    try:
        if os.getenv("KILL_PORT_PROCESS", "false").strip().lower() in {"1", "true", "yes"}:
            kill_process_on_port(port)
    except Exception:
        pass

    # Find available port if needed
    available_port = find_available_port(port)
    if available_port != port:
        logger.info(f"Port {port} busy, using port {available_port}")
        port = available_port

    if port is None:
        raise RuntimeError(f"No available ports found starting from {port}")

    # Start the API server
    cmd = [
        sys.executable, "-m", "uvicorn",
        "src.api.main:app",
        "--host", "127.0.0.1",
        "--port", str(port),
    ]
    # Enable reload only when explicitly requested (development)
    try:
        import os as _os
        if (_os.getenv("UVICORN_RELOAD", "false").strip().lower() in {"1", "true", "yes"}):
            cmd.append("--reload")
    except Exception:
        pass

    logger.info(f"Starting API server on port {port}")
    process = subprocess.Popen(cmd)

    # Wait for server to start
    max_wait = 30
    for i in range(max_wait):
        try:
            import requests
            # Try multiple health endpoints (prefer trailing slash)
            for url in (
                f"http://localhost:{port}/health/",
                f"http://localhost:{port}/health/system",
            ):
                try:
                    response = requests.get(url, timeout=2)
                    if 200 <= response.status_code < 300:
                        logger.info(f"API server started successfully on port {port}")
                        return process, port
                except Exception:
                    continue
        except Exception:
            pass

        if process.poll() is not None:
            # Process has terminated
            stdout, stderr = process.communicate()
            logger.error(f"API server failed to start: {stderr}")
            raise RuntimeError(f"API server failed: {stderr}")

        time.sleep(1)

    raise RuntimeError(f"API server failed to start within {max_wait} seconds")


def start_frontend_server(port: int = 3001, api_port: int = 8001) -> tuple[subprocess.Popen, int]:
    """Start the frontend server on the specified port."""
    # Optionally kill any existing process on the port (opt-in only)
    try:
        if os.getenv("KILL_PORT_PROCESS", "false").strip().lower() in {"1", "true", "yes"}:
            kill_process_on_port(port)
    except Exception:
        pass

    # Find available port if needed
    available_port = find_available_port(port)
    if available_port != port:
        logger.info(f"Port {port} busy, using port {available_port}")
        port = available_port

    if port is None:
        raise RuntimeError(f"No available ports found starting from {port}")

    # Change to frontend directory
    frontend_dir = Path(__file__).parent / "frontend" / "electron-react-app"

    # Start the frontend server
    cmd = [
        "cmd", "/c", "npm", "run", "start:renderer"
    ]

    env = {
        **os.environ,
        "PORT": str(port),
        "BROWSER": "none",
        "REACT_APP_API_URL": f"http://127.0.0.1:{api_port}",
    }

    logger.info(f"Starting frontend server on port {port}")
    process = subprocess.Popen(
        cmd,
        cwd=frontend_dir,
        env=env,
    )

    # Wait for server to start
    max_wait = 60
    for i in range(max_wait):
        try:
            import requests
            response = requests.get(f"http://localhost:{port}", timeout=2)
            if response.status_code == 200:
                logger.info(f"Frontend server started successfully on port {port}")
                return process, port
        except Exception:
            pass

        if process.poll() is not None:
            # Process has terminated
            stdout, stderr = process.communicate()
            logger.error(f"Frontend server failed to start: {stderr}")
            raise RuntimeError(f"Frontend server failed: {stderr}")

        time.sleep(1)

    raise RuntimeError(f"Frontend server failed to start within {max_wait} seconds")


async def main():
    """Main startup function."""
    try:
        # Configure logging
        settings = get_settings()
        configure_logging(settings.log_level)
        logger.info("Starting Therapy Compliance Analyzer with robust startup...")

        # Initialize database
        logger.info("Initializing database...")
        await init_db()

        # Initialize vector store
        logger.info("Initializing vector store...")
        vector_store = get_vector_store()

        # Initialize persistent task registry
        # NOTE: Blocking await is correct here - this is a standalone script
        # that needs services fully started before proceeding
        logger.info("Initializing persistent task registry...")
        await persistent_task_registry.cleanup_old_tasks(days_old=7)

        # Initialize enhanced worker manager
        # NOTE: Blocking await is correct here - not a web server startup
        logger.info("Starting enhanced worker manager...")
        await enhanced_worker_manager.start()

        logger.info("Enhanced core services started successfully!")

        # Determine starting ports from env (optional), default to 8001/3001
        try:
            api_start_port = int(os.getenv("API_PORT_START", "8001"))
        except Exception:
            api_start_port = 8001
        try:
            fe_start_port = int(os.getenv("FRONTEND_PORT_START", "3001"))
        except Exception:
            fe_start_port = 3001

        # Start API server (auto-finds a free port)
        api_process, api_port = await start_api_server(api_start_port)

        # Start frontend server (auto-finds a free port) unless explicitly skipped
        frontend_process = None
        frontend_port = None
        skip_fe = os.getenv("SKIP_FRONTEND", "false").strip().lower() in {"1", "true", "yes"}
        if not skip_fe:
            frontend_process, frontend_port = start_frontend_server(fe_start_port, api_port=api_port)

        logger.info("All services started successfully!")
        logger.info(f"API Server: http://localhost:{api_port}")
        if frontend_port is not None:
            logger.info(f"Frontend Server: http://localhost:{frontend_port}")
        logger.info(f"API Documentation: http://localhost:{api_port}/docs")

        # Keep running until interrupted
        try:
            while True:
                # Check if processes are still running
                if api_process.poll() is not None:
                    logger.error("API server stopped unexpectedly")
                    break

                if frontend_process is not None and frontend_process.poll() is not None:
                    logger.error("Frontend server stopped unexpectedly")
                    break

                await asyncio.sleep(1)

        except KeyboardInterrupt:
            logger.info("Shutdown requested by user")

        finally:
            # Graceful shutdown
            logger.info("Shutting down services...")

            if api_process.poll() is None:
                api_process.terminate()
                try:
                    api_process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    api_process.kill()

            if frontend_process is not None and frontend_process.poll() is None:
                frontend_process.terminate()
                try:
                    frontend_process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    frontend_process.kill()

            await enhanced_worker_manager.stop()
            await persistent_task_registry.close()
            logger.info("Shutdown complete")

        return True

    except Exception as e:
        logger.error("Startup failed", error=str(e))
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
