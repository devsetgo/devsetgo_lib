# -*- coding: utf-8 -*-
import pytest
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncEngine

from devsetgo_toolkit import DBConfig


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
