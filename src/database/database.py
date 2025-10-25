import logging
import sqlite3
from collections.abc import AsyncGenerator
from typing import Any

import requests
import sqlalchemy
import sqlalchemy.exc
from fastapi import Depends
from requests.exceptions import HTTPError
from sqlalchemy import text, event
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import StaticPool

from ..config import get_settings

logger = logging.getLogger(__name__)

# --- Database Configuration ---
settings = get_settings()
DATABASE_URL = settings.database.url


def get_database_url() -> str:
    """Get the database URL for connection."""
    return DATABASE_URL


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable SQLite foreign key constraints and other pragmas."""
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()


async def test_connection() -> bool:
    """Test database connection."""
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            return True
    except Exception as e:
        logger.error("Database connection test failed: %s", e)
        return False


# Ensure the URL is async-compatible for SQLite
if "sqlite" in DATABASE_URL and "aiosqlite" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://")


# --- Performance Configuration ---
def _get_performance_config() -> Any | None:
    """Safely get performance configuration with fallback."""
    # Temporarily disabled for faster startup
    logger.debug("Performance manager disabled for faster startup")
    return None


# Use performance manager if available, otherwise fall back to config settings
perf_config = _get_performance_config()
POOL_SIZE = (
    perf_config.connection_pool_size if perf_config else settings.database.pool_size
)
MAX_OVERFLOW = (
    perf_config.connection_pool_size * 2
    if perf_config
    else settings.database.max_overflow
)
POOL_TIMEOUT = settings.database.pool_timeout
POOL_RECYCLE = settings.database.pool_recycle

logger.info(
    "Database URL: %s", DATABASE_URL.split("///")[0] + "///<path>"
)  # Log without exposing full path
logger.info("Connection pool size: %s", POOL_SIZE)

# --- Engine Configuration ---
engine_args: dict[str, Any] = {
    "echo": settings.database.echo,
    "future": True,  # Use SQLAlchemy 2.0 style
}

# Configure connection pooling based on database type
if "sqlite" not in DATABASE_URL:
    # PostgreSQL, MySQL, etc. - use standard connection pooling
    logger.info("Configuring standard connection pooling for non-SQLite database")
    engine_args.update(
        {
            "pool_size": POOL_SIZE,
            "max_overflow": MAX_OVERFLOW,
            "pool_pre_ping": True,
            "pool_recycle": POOL_RECYCLE,
            "pool_timeout": POOL_TIMEOUT,
        }
    )
else:
    # SQLite-specific optimizations
    logger.info("Configuring SQLite-specific optimizations")
    engine_args.update(
        {
            "poolclass": StaticPool,
            "connect_args": {
                "check_same_thread": False,  # Required for async SQLite
                "timeout": settings.database.connection_timeout,
            },
            # For SQLite, we use a single connection pool
            "pool_pre_ping": True,
        }
    )

# --- Create Engine ---
engine = create_async_engine(DATABASE_URL, **engine_args)

# --- Session Factory ---
# Optimized session factory with proper configuration for medical data handling
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Keep objects accessible after commit
    autocommit=False,  # Explicit transaction control
    autoflush=False,  # Manual flush control for better performance
)

# --- Declarative Base ---
Base = declarative_base()


# --- Database Utilities ---
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that provides a transactional database session.

    Features:
    - Automatic transaction management with rollback on errors
    - Proper session cleanup to prevent connection leaks
    - Optimized for medical data processing workflows
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            # Only commit if no exception occurred
            await session.commit()
        except (sqlalchemy.exc.SQLAlchemyError, sqlite3.Error) as e:
            # Log the error for debugging (without PHI)
            logger.exception(
                "Database transaction failed, rolling back: %s", type(e).__name__
            )
            await session.rollback()
            raise
        finally:
            # Ensure session is always closed
            await session.close()


def get_db():
    """Get database session dependency for FastAPI."""
    return Depends(get_async_db)


async def init_db() -> None:
    """Initialize the database by creating all tables and applying optimizations.

    This function:
    - Creates all tables defined by SQLAlchemy models
    - Applies database-specific optimizations (SQLite pragmas, indexes)
    - Ensures proper schema setup for medical data compliance
    - Creates default admin user if none exists
    """
    logger.info("Initializing database schema")

    # Optional: run Alembic migrations if requested
    import os as _os
    if _os.getenv("USE_ALEMBIC", "false").strip().lower() in {"1", "true", "yes"}:
        try:
            from alembic.config import CommandLine as _AlembicCLI

            cli = _AlembicCLI(prog="alembic")
            cli.main(argv=["upgrade", "head"])  # raises SystemExit on success
            logger.info("Alembic migrations applied (upgrade head)")
        except Exception as _e:
            logger.warning("Alembic migration skipped or failed: %s", _e)

    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

        # Ensure preferences column exists for user table
        if "sqlite" in DATABASE_URL:
            result = await conn.execute(text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result.fetchall()]
            if "preferences" not in columns:
                logger.info("Adding preferences column to users table")
                await conn.execute(
                    text("ALTER TABLE users ADD COLUMN preferences JSON")
                )

        # Create default admin user if none exists
        result = await conn.execute(text("SELECT COUNT(*) FROM users"))
        if result.scalar() == 0:
            logger.info("Creating default admin user")
            # Use a proper session for ORM operations
            await create_default_admin_user()

        # Apply SQLite-specific optimizations if enabled
        if "sqlite" in DATABASE_URL and settings.database.sqlite_optimizations:
            logger.info("Applying SQLite performance optimizations")

            await conn.execute(
                text("PRAGMA journal_mode=WAL")
            )  # Write-Ahead Logging for better concurrency
            await conn.execute(
                text("PRAGMA synchronous=NORMAL")
            )  # Balance between safety and performance
            await conn.execute(
                text("PRAGMA cache_size=10000")
            )  # Increase cache size (10MB)
            await conn.execute(
                text("PRAGMA temp_store=MEMORY")
            )  # Store temp tables in memory
            await conn.execute(
                text("PRAGMA mmap_size=268435456")
            )  # Use memory mapping (256MB)
            await conn.execute(
                text("PRAGMA foreign_keys=ON")
            )  # Enable foreign key constraints

    logger.info("Database initialization complete")


async def create_default_admin_user() -> None:
    """Create a default admin user if none exists using an AsyncSession."""
    from src.database.models import User
    from passlib.context import CryptContext

    # Use CryptContext directly to avoid circular import
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async with AsyncSessionLocal() as session:
        default_admin = User(
            username="admin",
            hashed_password=pwd_context.hash("admin123"),
            is_active=True,
            is_admin=True,
        )
        session.add(default_admin)
        await session.commit()


async def close_db_connections() -> None:
    """Gracefully dispose of database engine and close all connections.

    This function ensures:
    - All active connections are properly closed
    - Connection pool is disposed of cleanly
    - No database locks remain after shutdown
    """
    logger.info("Shutting down database connections")
    try:
        await engine.dispose()
        logger.info("Database connections closed successfully")
    except (sqlalchemy.exc.SQLAlchemyError, sqlite3.Error) as e:
        logger.exception("Error during database shutdown: %s", e)
        raise


async def get_db_health() -> dict[str, Any]:
    """Check database health and return status information.

    Returns:
        Dict containing database health metrics and status

    """
    try:
        async with AsyncSessionLocal() as session:
            # Simple query to test connectivity
            result = await session.execute(text("SELECT 1"))
            result.fetchone()

            # Get basic stats if SQLite
            stats: dict[str, Any] = {
                "status": "healthy",
                "engine": str(engine.url).split("://")[0],
            }

            if "sqlite" in DATABASE_URL:
                # Get SQLite-specific stats
                pragma_results = await session.execute(text("PRAGMA database_list"))
                stats["databases"] = len(pragma_results.fetchall())

            return stats

    except (requests.RequestException, ConnectionError, TimeoutError, HTTPError) as e:
        logger.exception("Database health check failed: %s", e)
        return {"status": "unhealthy", "error": str(e)}


async def optimize_database() -> None:
    """Apply runtime database optimizations.

    This function can be called periodically to maintain optimal performance.
    """
    if "sqlite" not in DATABASE_URL or not settings.database.sqlite_optimizations:
        return

    try:
        async with AsyncSessionLocal() as session:
            logger.info("Running database optimization")

            # Analyze tables for better query planning
            await session.execute(text("ANALYZE"))

            # Vacuum if needed (reclaim space)
            result = await session.execute(text("PRAGMA auto_vacuum"))
            auto_vacuum = result.scalar()

            if auto_vacuum == 0:  # None
                await session.execute(text("VACUUM"))
                logger.info("Database vacuum completed")

            await session.commit()

    except (sqlalchemy.exc.SQLAlchemyError, sqlite3.Error) as e:
        logger.exception("Database optimization failed: %s", e)


# --- Connection Management Utilities ---
# test_connection function already defined above
