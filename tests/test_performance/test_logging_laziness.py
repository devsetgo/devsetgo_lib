# -*- coding: utf-8 -*-
"""
The library's own log calls must cost (almost) nothing when their level is
disabled. These tests prove that expensive arguments -- SQL statements,
result sets, per-record dicts, locals() -- are never stringified unless the
devsetgo_lib logger will actually emit the record.
"""
import logging

import pytest
from sqlalchemy import Column, Integer, String, select
from sqlalchemy.sql.elements import TextClause

from dsg_lib import LOGGER
from dsg_lib.async_database_functions.async_database import AsyncDatabase
from dsg_lib.async_database_functions.database_config import DBConfig
from dsg_lib.async_database_functions.database_operations import DatabaseOperations
from dsg_lib.common_functions.email_validation import validate_email_address

async_db = AsyncDatabase(
    DBConfig({"database_uri": "sqlite+aiosqlite:///:memory:"})
)
db_ops = DatabaseOperations(async_db)


class LazyUser(async_db.Base):
    __tablename__ = "lazy_users"
    pkid = Column(Integer, primary_key=True)
    name = Column(String)


class CountingText(TextClause):
    """A SQL text clause that counts how often logging stringifies it."""

    inherit_cache = True
    str_calls = 0

    def __str__(self):
        CountingText.str_calls += 1
        return super().__str__()


class ListHandler(logging.Handler):
    def __init__(self):
        super().__init__(logging.DEBUG)
        self.messages = []

    def emit(self, record):
        self.messages.append(record.getMessage())

    @property
    def text(self):
        return "\n".join(self.messages)


@pytest.fixture
def lib_level():
    """
    Set the devsetgo_lib logger level for one test and capture what it emits.
    (tests/conftest.py overrides caplog with a loguru-specific fixture, so a
    plain handler is used here instead.)
    """
    previous = LOGGER.level
    handler = ListHandler()
    LOGGER.addHandler(handler)

    def _set(level):
        LOGGER.setLevel(level)
        return handler

    yield _set
    LOGGER.removeHandler(handler)
    LOGGER.setLevel(previous)


@pytest.mark.asyncio
async def test_read_query_does_not_stringify_query_when_debug_off(lib_level):
    lib_level(logging.WARNING)
    CountingText.str_calls = 0
    result = await db_ops.read_query(CountingText("SELECT 1"))
    assert result == [1]
    assert CountingText.str_calls == 0


@pytest.mark.asyncio
async def test_read_query_stringifies_query_when_debug_on(lib_level):
    captured = lib_level(logging.DEBUG)
    CountingText.str_calls = 0
    await db_ops.read_query(CountingText("SELECT 1"))
    assert CountingText.str_calls >= 1
    assert "Executing fetch query: SELECT 1" in captured.text


@pytest.mark.asyncio
@pytest.mark.parametrize("level", [logging.WARNING, logging.DEBUG])
async def test_create_many_record_dicts_only_built_for_debug(lib_level, level):
    await async_db.create_tables()
    captured = lib_level(level)
    records = await db_ops.create_many([LazyUser(name="a"), LazyUser(name="b")])
    assert len(records) == 2
    assert ("Records added to session" in captured.text) is (level == logging.DEBUG)
    rows = await db_ops.read_query(select(LazyUser.name))
    assert set(rows) >= {"a", "b"}


@pytest.mark.parametrize("level", [logging.WARNING, logging.DEBUG])
def test_validate_email_params_only_logged_for_debug(lib_level, level):
    captured = lib_level(level)
    result = validate_email_address("someone@example.com", check_deliverability=False)
    assert result["valid"] is True
    assert ("with params" in captured.text) is (level == logging.DEBUG)
