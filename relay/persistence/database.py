"""SQLAlchemy engine and session setup for the local PostgreSQL store."""

from __future__ import annotations

import os

from sqlalchemy import Engine, create_engine as sqlalchemy_create_engine
from sqlalchemy.orm import Session, sessionmaker


DATABASE_URL_ENV = "RELAY_DATABASE_URL"


def get_database_url() -> str:
    """Return the configured database URL or explain the required setting."""

    database_url = os.environ.get(DATABASE_URL_ENV)
    if not database_url:
        raise RuntimeError(
            f"Set {DATABASE_URL_ENV} to a PostgreSQL connection URL, "
            "for example postgresql+psycopg://user:password@localhost/relay."
        )
    return database_url


def create_engine(database_url: str | None = None) -> Engine:
    """Create an engine for an explicit URL or the local configured URL."""

    return sqlalchemy_create_engine(database_url or get_database_url())


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Create sessions bound to *engine*, with explicit transaction control."""

    return sessionmaker(bind=engine, expire_on_commit=False)
