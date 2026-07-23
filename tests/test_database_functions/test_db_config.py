# -*- coding: utf-8 -*-
import pytest
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import sessionmaker

from dsg_lib.async_database_functions.database_config import DBConfig


def test_sqlite_supported_parameters():
    config = {
        "database_uri": "sqlite+aiosqlite:///:memory:",
        "echo": True,
        "future": True,
        "pool_recycle": 3600,
    }
    db_config = DBConfig(config)
    assert isinstance(db_config.engine, AsyncEngine)
    assert isinstance(db_config.metadata, MetaData)


def test_sqlite_unsupported_parameters():
    config = {
        "database_uri": "sqlite+aiosqlite:///:memory:?cache=shared",
        "pool_size": 5,
        "max_overflow": 10,
        "pool_timeout": 30,
    }
    with pytest.raises(Exception):
        DBConfig(config)


def test_postgresql_supported_parameters():
    config = {
        "database_uri": "postgresql+asyncpg://postgres:postgres@db/postgres",
        "echo": True,
        "future": True,
        "pool_pre_ping": True,
        "pool_size": 5,
        "max_overflow": 10,
        "pool_recycle": 3600,
        "pool_timeout": 30,
    }
    db_config = DBConfig(config)
    assert isinstance(db_config.engine, AsyncEngine)
    assert isinstance(db_config.metadata, MetaData)


def test_postgresql_unsupported_parameters():
    config = {
        "database_uri": "postgresql+asyncpg://postgres:postgres@db/postgres",
        "unsupported_option": True,
    }
    with pytest.raises(Exception):
        DBConfig(config)


def test_sqlite_common_parameters():
    # connect_args/isolation_level are dialect-agnostic and should be accepted
    # even though they aren't in SQLite's own SUPPORTED_PARAMETERS set.
    config = {
        "database_uri": "sqlite+aiosqlite:///:memory:",
        "echo": True,
        "connect_args": {"timeout": 5},
        "isolation_level": "SERIALIZABLE",
    }
    db_config = DBConfig(config)
    assert isinstance(db_config.engine, AsyncEngine)
    assert db_config.engine.dialect.name == "sqlite"


def test_postgresql_common_parameters():
    config = {
        "database_uri": "postgresql+asyncpg://postgres:postgres@db/postgres",
        "echo": True,
        "connect_args": {"timeout": 5},
        "execution_options": {"isolation_level": "AUTOCOMMIT"},
        "isolation_level": "SERIALIZABLE",
        "query_cache_size": 100,
        "hide_parameters": True,
    }
    db_config = DBConfig(config)
    assert isinstance(db_config.engine, AsyncEngine)
    assert db_config.engine.dialect.name == "postgresql"


def test_common_parameters_do_not_bypass_dialect_specific_validation():
    # A common parameter alongside a genuinely unsupported one should still raise.
    config = {
        "database_uri": "sqlite+aiosqlite:///:memory:",
        "connect_args": {},
        "unsupported_option": True,
    }
    with pytest.raises(Exception):
        DBConfig(config)


@pytest.mark.parametrize(
    "database_uri,expected_dialect",
    [
        ("sqlite+aiosqlite:///:memory:", "sqlite"),
        ("postgresql+asyncpg://user:pass@host/db", "postgresql"),
        ("mysql+asyncmy://user:pass@host/db", "mysql"),
        ("oracle+oracledb://user:pass@host/db", "oracle"),
        ("cockroachdb+asyncpg://user:pass@host/db", "cockroachdb"),
        ("mssql+aioodbc://user:pass@host/db", "mssql"),
    ],
)
def test_dialect_detection_across_backends(database_uri, expected_dialect):
    # Exercises make_url(...).get_backend_name() dialect detection (used to
    # select the right SUPPORTED_PARAMETERS entry) across every backend that
    # has an importable async driver in this environment.
    db_config = DBConfig({"database_uri": database_uri, "connect_args": {}})
    assert db_config.engine.dialect.name == expected_dialect


def test_session_factory_is_built_once_in_init():
    # Performance fix: the sessionmaker factory must be built once in
    # __init__, not reconstructed on every get_db_session() call.
    db_config = DBConfig({"database_uri": "sqlite+aiosqlite:///:memory:"})
    assert isinstance(db_config._session_factory, sessionmaker)


async def test_get_db_session_reuses_cached_factory_but_yields_new_sessions():
    db_config = DBConfig({"database_uri": "sqlite+aiosqlite:///:memory:"})
    factory = db_config._session_factory

    async with db_config.get_db_session() as session1:
        assert isinstance(session1, AsyncSession)

    async with db_config.get_db_session() as session2:
        assert isinstance(session2, AsyncSession)

    # The factory itself is never rebuilt between calls...
    assert db_config._session_factory is factory
    # ...but each call still yields its own distinct session.
    assert session1 is not session2
