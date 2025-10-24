from __future__ import annotations

import os
from logging.config import fileConfig

from sqlalchemy import create_engine
from sqlalchemy import pool
from alembic import context

# this is the Alembic Config object, which provides access to the values within
# the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import metadata from the application
from src.database.database import Base  # noqa: E402
from src.config import get_settings  # noqa: E402

target_metadata = Base.metadata


def get_sync_url() -> str:
    """Return a synchronous SQLAlchemy URL suitable for Alembic engine."""
    settings = get_settings()
    url = settings.database.url
    if url.startswith("sqlite+"):
        # aiosqlite -> sqlite
        url = url.replace("sqlite+aiosqlite://", "sqlite:///")
        url = url.replace("sqlite+pysqlite://", "sqlite:///")
    return url


def run_migrations_offline() -> None:
    url = get_sync_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(get_sync_url(), poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

