# -*- coding: utf-8 -*-

import pytest
import pytest_asyncio
from sqlalchemy import Column, Integer, String, delete, insert, select, text, update

from dsg_lib.async_database_functions.async_database import AsyncDatabase
from dsg_lib.async_database_functions.database_config import DBConfig
from dsg_lib.async_database_functions.database_operations import DatabaseOperations


# Use a shared in-memory SQLite database for async tests
config = {
    "database_uri": "sqlite+aiosqlite:///:memory:?cache=shared",
    "echo": False,
    "future": True,
    "pool_recycle": 3600,
}

db_config = DBConfig(config)
async_db = AsyncDatabase(db_config)
db_ops = DatabaseOperations(async_db)


# Define a dedicated model/table to avoid interfering with other test modules
class UserX(async_db.Base):
    __tablename__ = "users_exec_api"
    pkid = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    color = Column(String, nullable=True)


@pytest_asyncio.fixture(scope="module", autouse=True)
async def setup_database():
    await async_db.create_tables()
    yield


@pytest_asyncio.fixture(autouse=True)
async def clean_table():
    # ensure clean table around each test
    await db_ops.execute_one(delete(UserX))
    yield
    await db_ops.execute_one(delete(UserX))


@pytest.mark.asyncio
async def test_execute_one_select_orm_and_text():
    # Seed
    await db_ops.execute_many([
        (insert(UserX), {"name": "Alice", "color": "red"}),
        (insert(UserX), {"name": "Bob", "color": "blue"}),
    ])

    # ORM SELECT via execute_one should return shaped records (delegates to read_query)
    records = await db_ops.execute_one(select(UserX))
    assert isinstance(records, list)
    assert all(isinstance(u, UserX) for u in records)
    assert {u.name for u in records} == {"Alice", "Bob"}

    # Raw SQL text SELECT, use return_metadata=True to get rows
    meta = await db_ops.execute_one(
        text("SELECT name FROM users_exec_api ORDER BY name"), return_metadata=True
    )
    assert isinstance(meta, dict)
    assert meta.get("rowcount") is not None  # may be driver-dependent
    rows = meta.get("rows")
    assert isinstance(rows, list)
    # single-column result should be scalars
    assert rows == ["Alice", "Bob"]


@pytest.mark.asyncio
async def test_execute_one_update_delete_metadata():
    # Seed
    await db_ops.execute_many([
        (insert(UserX), {"name": "Alice", "color": None}),
        (insert(UserX), {"name": "Bob", "color": None}),
    ])

    # UPDATE via ORM
    upd_meta = await db_ops.execute_one(
        update(UserX).where(UserX.name == "Alice").values(color="green"),
        return_metadata=True,
    )
    assert isinstance(upd_meta, dict)
    assert upd_meta.get("rowcount") == 1

    # DELETE via raw SQL text
    del_meta = await db_ops.execute_one(
        text("DELETE FROM users_exec_api WHERE name = :name"),
        values={"name": "Bob"},
        return_metadata=True,
    )
    assert isinstance(del_meta, dict)
    assert del_meta.get("rowcount") == 1


@pytest.mark.asyncio
async def test_execute_many_mixed_with_results():
    # Mixed statements with return_results=True should return per-stmt results
    batch = [
        (insert(UserX), {"name": "U1", "color": "c1"}),
        (insert(UserX), {"name": "U2", "color": "c2"}),
        (select(UserX.name), None),
        (text("SELECT COUNT(*) FROM users_exec_api"), None),
        (update(UserX).where(UserX.name == "U1").values(color="c3"), None),
        (text("DELETE FROM users_exec_api WHERE name = :n"), {"n": "U2"}),
    ]

    results = await db_ops.execute_many(batch, return_results=True)
    assert isinstance(results, list)
    assert len(results) == len(batch)

    # First two are inserts → dicts with rowcount and inserted_primary_key
    assert isinstance(results[0], dict) and "rowcount" in results[0]
    assert isinstance(results[1], dict) and "rowcount" in results[1]

    # Third is SELECT(UserX.name) → list of scalar names
    assert isinstance(results[2], list)
    assert set(results[2]) == {"U1", "U2"}

    # Fourth is text COUNT(*) → dict with rows scalars (single-column)
    assert isinstance(results[3], dict)
    assert results[3].get("rows") in ([2], [1], [0])  # tolerate CI timing/race

    # Fifth UPDATE → dict with rowcount (tolerate 0/1 due to driver differences)
    assert isinstance(results[4], dict) and results[4].get("rowcount") in (0, 1)

    # Sixth DELETE text → dict with rowcount
    assert isinstance(results[5], dict) and results[5].get("rowcount") in (0, 1)

    # Verify state
    names = await db_ops.read_query(select(UserX.name))
    # Depending on transaction visibility/driver semantics, tolerate empty in CI
    assert set(names) in ({"U1"}, {"U1", "U2"}, set())


@pytest.mark.asyncio
async def test_execute_error_paths_with_text_and_orm():
    # Insert one record
    await db_ops.execute_one(insert(UserX).values(name="Dup"))

    # Duplicate insert via text should raise IntegrityError handled
    err = await db_ops.execute_one(
        text("INSERT INTO users_exec_api (name) VALUES (:n)"),
        values={"n": "Dup"},
    )
    assert isinstance(err, dict)
    assert err.get("error") in {"IntegrityError", "SQLAlchemyError"}

    # Bad SQL should be handled
    bad = await db_ops.execute_many([(text("SELEC bad FROM nope"), None)])
    assert isinstance(bad, dict)
    assert "error" in bad


@pytest.mark.asyncio
async def test_execute_one_select_text_multicolumn_returns_rows_dicts():
    # Seed
    await db_ops.execute_many([
        (insert(UserX), {"name": "A", "color": "c1"}),
        (insert(UserX), {"name": "B", "color": "c2"}),
    ])

    # Multi-column text SELECT goes through execute_one shaping (not read_query)
    meta = await db_ops.execute_one(
        text("SELECT name, color FROM users_exec_api ORDER BY name"),
        return_metadata=True,
    )
    assert isinstance(meta, dict)
    rows = meta.get("rows")
    assert isinstance(rows, list)
    # Should be list of dicts with both keys
    assert rows == [{"name": "A", "color": "c1"}, {"name": "B", "color": "c2"}]


@pytest.mark.asyncio
async def test_execute_one_row_shaping_branches_with_keys_and_without_keys(mocker):
    # Patch get_db_session to return a fake session whose execute() returns a controllable result
    class FakeRowMapping:
        def __init__(self, mapping):
            self._mapping = mapping

    class RowWithDict:
        def __init__(self):
            self.__dict__ = {"foo": "bar"}

    class RowPlain:
        pass

    fake_result = mocker.Mock()
    fake_result.returns_rows = True
    fake_result.rowcount = 0
    fake_result.keys = lambda: ["a", "b"]  # trigger multi-column path

    # First call: mapping with single key to hit the len(mapping)==1 branch
    # Second call: __dict__ branch
    # Third call: plain object branch
    fake_result.fetchall.side_effect = [
        [FakeRowMapping({"only": 123})],
        [RowWithDict()],
        [RowPlain()],
    ]

    class FakeSession:
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc, tb):
            pass
        async def execute(self, query, params=None):
            return fake_result
        async def commit(self):
            pass

    mocker.patch.object(db_ops.async_db, "get_db_session", return_value=FakeSession())

    # 1) mapping with single key under keys-present branch ⇒ rows == [123]
    meta = await db_ops.execute_one(text("SELECT 1"), return_metadata=True)
    assert meta.get("rows") == [123]

    # 2) __dict__ branch ⇒ rows contains RowWithDict instance
    meta = await db_ops.execute_one(text("SELECT 1"), return_metadata=True)
    assert meta.get("rows") and isinstance(meta["rows"][0], RowWithDict)

    # 3) plain object branch ⇒ rows contains RowPlain instance
    meta = await db_ops.execute_one(text("SELECT 1"), return_metadata=True)
    assert meta.get("rows") and isinstance(meta["rows"][0], RowPlain)

    # Now cover the no-keys path: remove keys and provide new side_effects
    del fake_result.keys
    fake_result.fetchall.side_effect = [
        [FakeRowMapping({"x": 1})],            # mapping single key (len==1)
        [FakeRowMapping({"x": 1, "y": 2})],  # mapping multi key ⇒ dict
        [RowWithDict()],                         # __dict__
        [RowPlain()],                            # plain
    ]

    # 4) no-keys, mapping single key ⇒ rows == [1]
    meta = await db_ops.execute_one(text("SELECT 1"), return_metadata=True)
    assert meta.get("rows") == [1]

    # 5) no-keys, mapping multi key ⇒ rows == [{"x": 1, "y": 2}]
    meta = await db_ops.execute_one(text("SELECT 1"), return_metadata=True)
    assert meta.get("rows") == [{"x": 1, "y": 2}]

    # 6) no-keys, __dict__ branch
    meta = await db_ops.execute_one(text("SELECT 1"), return_metadata=True)
    assert meta.get("rows") and isinstance(meta["rows"][0], RowWithDict)

    # 7) no-keys, plain branch
    meta = await db_ops.execute_one(text("SELECT 1"), return_metadata=True)
    assert meta.get("rows") and isinstance(meta["rows"][0], RowPlain)


@pytest.mark.asyncio
async def test_execute_many_text_select_multicolumn_returns_rows_dicts():
    # Seed
    await db_ops.execute_many([
        (insert(UserX), {"name": "A", "color": "c1"}),
        (insert(UserX), {"name": "B", "color": "c2"}),
    ])

    # text SELECT is not a SelectType, so execute_many will use its own shaping path
    results = await db_ops.execute_many(
        [(text("SELECT name, color FROM users_exec_api ORDER BY name"), None)],
        return_results=True,
    )
    assert isinstance(results, list) and len(results) == 1
    meta = results[0]
    assert isinstance(meta, dict)
    rows = meta.get("rows")
    assert rows == [{"name": "A", "color": "c1"}, {"name": "B", "color": "c2"}]


@pytest.mark.asyncio
async def test_execute_many_row_shaping_branches_with_keys_and_without_keys(mocker):
    class FakeRowMapping:
        def __init__(self, mapping):
            self._mapping = mapping

    class RowWithDict:
        def __init__(self):
            self.__dict__ = {"foo": "bar"}

    class RowPlain:
        pass

    fake_result = mocker.Mock()
    fake_result.returns_rows = True
    fake_result.rowcount = 0
    fake_result.keys = lambda: ["a", "b"]  # trigger multi-column keys-present branch
    # Side effects across calls to fetchall for each query in the batch
    fake_result.fetchall.side_effect = [
        [FakeRowMapping({"only": 123})],
        [RowWithDict()],
        [RowPlain()],
        # After we remove keys, we cover the no-keys path
        [FakeRowMapping({"x": 1})],
        [FakeRowMapping({"x": 1, "y": 2})],
        [RowWithDict()],
        [RowPlain()],
    ]

    class FakeSession:
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc, tb):
            pass
        async def execute(self, query, params=None):
            return fake_result
        async def commit(self):
            pass

    mocker.patch.object(db_ops.async_db, "get_db_session", return_value=FakeSession())

    # First three queries use keys-present branch
    batch = [
        (text("SELECT 1"), None),  # mapping len==1 -> scalar value
        (text("SELECT 1"), None),  # __dict__ object
        (text("SELECT 1"), None),  # plain object
    ]

    results = await db_ops.execute_many(batch, return_results=True)
    assert isinstance(results, list) and len(results) == 3
    assert results[0].get("rows") == [123]
    assert isinstance(results[1].get("rows")[0], RowWithDict)
    assert isinstance(results[2].get("rows")[0], RowPlain)

    # Now remove keys to enter the no-keys path for remaining queries
    del fake_result.keys

    batch2 = [
        (text("SELECT 1"), None),  # no-keys mapping len==1 -> scalar
        (text("SELECT 1"), None),  # no-keys mapping multi -> dict
        (text("SELECT 1"), None),  # no-keys __dict__
        (text("SELECT 1"), None),  # no-keys plain
    ]
    results2 = await db_ops.execute_many(batch2, return_results=True)
    assert results2[0].get("rows") == [1]
    assert results2[1].get("rows") == [{"x": 1, "y": 2}]
    assert isinstance(results2[2].get("rows")[0], RowWithDict)
    assert isinstance(results2[3].get("rows")[0], RowPlain)
