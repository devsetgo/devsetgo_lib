# -*- coding: utf-8 -*-
import asyncio
import secrets

import pytest
from sqlalchemy import Column, Integer, String, delete, insert, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from dsg_lib.async_database_functions.async_database import AsyncDatabase
from dsg_lib.async_database_functions.database_config import DBConfig
from dsg_lib.async_database_functions.database_operations import DatabaseOperations

config = {
    "database_uri": "sqlite+aiosqlite:///:memory:?cache=shared",
    "echo": True,
    "future": True,
    "pool_recycle": 3600,
}
db_config = DBConfig(config)
async_db = AsyncDatabase(db_config)
db_ops = DatabaseOperations(async_db)


# Define User class here
class User(async_db.Base):
    __tablename__ = "users"
    pkid = Column(Integer, primary_key=True)
    name = Column(String, unique=True)


class TestDatabaseOperations:
    @pytest.fixture(scope="session")
    def db_ops(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(async_db.create_tables())
        return db_ops

    @pytest.mark.asyncio
    async def test_count_query(self, db_ops):
        # db_ops is already awaited by pytest, so you can use it directly
        users = [User(name=f"User{i}-{secrets.token_hex(2)}") for i in range(10)]
        result = await db_ops.create_many(users)
        assert len(result) == 10

        # get all pkids from results
        pkids = [user.pkid for user in result]
        assert len(pkids) == 10

        # Create a Select object that selects all rows from the User table
        query = select(User)

        # count the users
        count = await db_ops.count_query(query)
        assert count == 10

    @pytest.mark.asyncio
    async def test_count_query_sqlalchemy_error(self, db_ops, mocker):
        # Mock the get_db_session method to raise an SQLAlchemyError
        mocker.patch.object(
            db_ops.async_db,
            "get_db_session",
            side_effect=SQLAlchemyError("Test error message"),
        )

        # Check that count_query returns an error dictionary
        result = await db_ops.count_query(select(User))
        assert result == {"error": "SQLAlchemyError", "details": "Test error message"}

    @pytest.mark.asyncio
    async def test_count_query_general_exception(self, db_ops, mocker):
        # Mock the get_db_session method to raise an Exception
        mocker.patch.object(
            db_ops.async_db,
            "get_db_session",
            side_effect=Exception("Test error message"),
        )

        # Check that count_query returns an error dictionary
        result = await db_ops.count_query(select(User))
        assert result == {"error": "General Exception", "details": "Test error message"}

    @pytest.mark.asyncio
    async def test_read_query(self, db_ops):
        # db_ops is already awaited by pytest, so you can use it directly
        user = User(name="Mike")
        await db_ops.create_one(user)
        data = await db_ops.read_query(select(User))
        assert isinstance(data, list)
        assert len(data) > 0

    @pytest.mark.asyncio
    async def test_read_query_sqlalchemy_error(self, db_ops, mocker):
        # Mock the get_db_session method to raise an SQLAlchemyError
        mocker.patch.object(
            db_ops.async_db,
            "get_db_session",
            side_effect=SQLAlchemyError("Test error message"),
        )

        # Check that read_query returns an error dictionary
        result = await db_ops.read_query(select(User))
        assert result == {"error": "SQLAlchemyError", "details": "Test error message"}

    @pytest.mark.asyncio
    async def test_read_query_general_exception(self, db_ops, mocker):
        # Mock the get_db_session method to raise an Exception
        mocker.patch.object(
            db_ops.async_db,
            "get_db_session",
            side_effect=Exception("Test error message"),
        )

        # Check that read_query returns an error dictionary
        result = await db_ops.read_query(select(User))
        assert result == {"error": "General Exception", "details": "Test error message"}

    @pytest.mark.asyncio
    async def test_read_multi_query(self, db_ops):
        # db_ops is already awaited by pytest, so you can use it directly
        queries = {"all_users": select(User)}
        results = await db_ops.read_multi_query(queries)
        assert isinstance(results, dict)
        assert "all_users" in results
        assert isinstance(results["all_users"], list)

    @pytest.mark.asyncio
    async def test_read_multi_query_sqlalchemy_error(self, db_ops, mocker):
        # Mock the get_db_session method to raise an SQLAlchemyError
        mocker.patch.object(
            db_ops.async_db,
            "get_db_session",
            side_effect=SQLAlchemyError("Test error message"),
        )

        # Check that read_multi_query returns an error dictionary
        queries = {"test_query": select(User)}
        result = await db_ops.read_multi_query(queries)
        assert result == {"error": "SQLAlchemyError", "details": "Test error message"}

    @pytest.mark.asyncio
    async def test_read_multi_query_general_exception(self, db_ops, mocker):
        # Mock the get_db_session method to raise an Exception
        mocker.patch.object(
            db_ops.async_db,
            "get_db_session",
            side_effect=Exception("Test error message"),
        )

        # Check that read_multi_query returns an error dictionary
        queries = {"test_query": select(User)}
        result = await db_ops.read_multi_query(queries)
        assert result == {"error": "General Exception", "details": "Test error message"}

    @pytest.mark.asyncio
    async def test_create_one(self, db_ops):
        # db_ops is already awaited by pytest, so you can use it directly
        user_name = f"Mike{secrets.randbelow(100000)}"
        user = User(name=user_name)
        result = await db_ops.create_one(user)
        assert isinstance(result, User)
        assert result.name == user_name

    @pytest.mark.asyncio
    async def test_create_one_sqlalchemy_error(self, db_ops, mocker):
        # Mock the get_db_session method to raise an SQLAlchemyError
        mocker.patch.object(
            db_ops.async_db,
            "get_db_session",
            side_effect=SQLAlchemyError("Test error message"),
        )

        # Check that create_one returns an error dictionary
        result = await db_ops.create_one(User(name="test"))
        assert result == {"error": "SQLAlchemyError", "details": "Test error message"}

    @pytest.mark.asyncio
    async def test_create_one_general_exception(self, db_ops, mocker):
        # Mock the get_db_session method to raise an Exception
        mocker.patch.object(
            db_ops.async_db,
            "get_db_session",
            side_effect=Exception("Test error message"),
        )

        # Check that create_one returns an error dictionary
        result = await db_ops.create_one(User(name="test"))
        assert result == {"error": "General Exception", "details": "Test error message"}

    @pytest.mark.asyncio
    async def test_create_one_integrity_error(self, db_ops, mocker):
        # Mock the get_db_session method to raise an IntegrityError
        mocker.patch.object(
            db_ops.async_db,
            "get_db_session",
            side_effect=IntegrityError(None, None, "Test error message"),
        )

        # Check that create_one returns an error dictionary
        result = await db_ops.create_one(User(name="test"))
        assert result == {
            "error": "IntegrityError",
            "details": "(builtins.str) Test error message\n(Background on this error at: https://sqlalche.me/e/20/gkpj)",
        }

    @pytest.mark.asyncio
    async def test_create_many(self, db_ops):
        # db_ops is already awaited by pytest, so you can use it directly
        users = [User(name=f"User{i}") for i in range(10)]
        result = await db_ops.create_many(users)
        assert isinstance(result, list)
        assert len(result) == 10

    @pytest.mark.asyncio
    async def test_create_many_sqlalchemy_error(self, db_ops, mocker):
        # Mock the get_db_session method to raise an SQLAlchemyError
        mocker.patch.object(
            db_ops.async_db,
            "get_db_session",
            side_effect=SQLAlchemyError("Test error message"),
        )

        # Check that create_many returns an error dictionary
        result = await db_ops.create_many([User(name="test1"), User(name="test2")])
        assert result == {"error": "SQLAlchemyError", "details": "Test error message"}

    @pytest.mark.asyncio
    async def test_create_many_general_exception(self, db_ops, mocker):
        # Mock the get_db_session method to raise an Exception
        mocker.patch.object(
            db_ops.async_db,
            "get_db_session",
            side_effect=Exception("Test error message"),
        )

        # Check that create_many returns an error dictionary
        result = await db_ops.create_many([User(name="test1"), User(name="test2")])
        assert result == {"error": "General Exception", "details": "Test error message"}

    @pytest.mark.asyncio
    async def test_create_many_integrity_error(self, db_ops, mocker):
        # Mock the get_db_session method to raise an IntegrityError
        mocker.patch.object(
            db_ops.async_db,
            "get_db_session",
            side_effect=IntegrityError(None, None, None, None),
        )

        # Check that create_many returns an error dictionary
        result = await db_ops.create_many([User(name="test1"), User(name="test2")])
        assert result["error"] == "IntegrityError"  # Corrected spelling
        assert isinstance(result["details"], str)
        assert result["details"] != ""

    @pytest.mark.asyncio
    async def test_update_one(self, db_ops):
        # db_ops is already awaited by pytest, so you can use it directly
        name = f"Mike{secrets.randbelow(1000)}"
        user = User(name=name)
        user_record = await db_ops.create_one(user)
        updated_user = {"name": "John12345"}
        result = await db_ops.update_one(
            table=User, record_id=user_record.pkid, new_values=updated_user
        )
        assert isinstance(result, User)
        assert result.name == "John12345"

    @pytest.mark.asyncio
    async def test_update_one_record_not_found(self, db_ops):
        # Check that update_one returns an error dictionary when no record is found
        result = await db_ops.update_one(
            table=User, record_id=9999, new_values={"name": "test"}
        )
        assert result == {
            "error": "Record not found",
            "details": "No record found with pkid 9999",
        }

    @pytest.mark.asyncio
    async def test_update_one_integrity_error(self, db_ops, mocker):
        # Mock the get_db_session method to raise an IntegrityError
        mocker.patch.object(
            db_ops.async_db,
            "get_db_session",
            side_effect=IntegrityError(None, None, "Test error message"),
        )

        # Check that update_one returns an error dictionary
        updated_user = {"name": "John12345", "pkid": "bob"}
        result = await db_ops.update_one(
            table=User, record_id=1, new_values=updated_user
        )
        assert result == {
            "error": "IntegrityError",
            "details": "(builtins.str) Test error message\n(Background on this error at: https://sqlalche.me/e/20/gkpj)",
        }

    @pytest.mark.asyncio
    async def test_update_one_sqlalchemy_error(self, db_ops, mocker):
        # Mock the get_db_session method to raise an SQLAlchemyError
        mocker.patch.object(
            db_ops.async_db,
            "get_db_session",
            side_effect=SQLAlchemyError("Test error message"),
        )

        # Check that update_one returns an error dictionary
        result = await db_ops.update_one(
            table=User, record_id=1, new_values={"name": "test"}
        )
        assert result == {
            "error": "SQLAlchemyError",
            "details": "Test error message",
        }

    @pytest.mark.asyncio
    async def test_update_one_general_exception(self, db_ops, mocker):
        # Mock the get_db_session method to raise an Exception
        mocker.patch.object(
            db_ops.async_db,
            "get_db_session",
            side_effect=Exception("Test error message"),
        )

        # Check that update_one returns an error dictionary
        result = await db_ops.update_one(
            table=User, record_id=1, new_values={"name": "test"}
        )
        assert result == {"error": "General Exception", "details": "Test error message"}

    @pytest.mark.asyncio
    async def test_delete_one(self, db_ops):
        # db_ops is already awaited by pytest, so you can use it directly
        user = User(name="Mike12345")
        user_record = await db_ops.create_one(user)
        result = await db_ops.delete_one(table=User, record_id=user_record.pkid)
        assert result == {"success": "Record deleted successfully"}

    @pytest.mark.asyncio
    async def test_delete_one_record_not_found(self, db_ops):
        # Check that delete_one returns an error dictionary when no record is found
        result = await db_ops.delete_one(table=User, record_id=9999)
        assert result == {
            "error": "Record not found",
            "details": "No record found with pkid 9999",
        }

    @pytest.mark.asyncio
    async def test_delete_one_sqlalchemy_error(self, db_ops, mocker):
        # Mock the get_db_session method to raise an SQLAlchemyError
        mocker.patch.object(
            db_ops.async_db,
            "get_db_session",
            side_effect=SQLAlchemyError("Test error message"),
        )

        # Check that delete_one returns an error dictionary
        result = await db_ops.delete_one(table=User, record_id=1)
        assert result == {"error": "SQLAlchemyError", "details": "Test error message"}

    @pytest.mark.asyncio
    async def test_delete_one_general_exception(self, db_ops, mocker):
        # Mock the get_db_session method to raise an Exception
        mocker.patch.object(
            db_ops.async_db,
            "get_db_session",
            side_effect=Exception("Test error message"),
        )

        # Check that delete_one returns an error dictionary
        result = await db_ops.delete_one(table=User, record_id=1)
        assert result == {"error": "General Exception", "details": "Test error message"}

    @pytest.mark.asyncio
    async def test_get_table_names(self, db_ops):
        tables = await db_ops.get_table_names()
        assert len(tables) <= 1

    @pytest.mark.asyncio
    async def test_get_column_details(self, db_ops):
        column_details = await db_ops.get_columns_details(User)
        assert isinstance(column_details, dict)

    @pytest.mark.asyncio
    async def test_get_primary_keys(self, db_ops):
        keys = await db_ops.get_primary_keys(User)
        assert isinstance(keys, list)

    @pytest.mark.asyncio
    async def test_read_one_record(self, db_ops):
        user_name = f"Mike{secrets.randbelow(1000)}"
        user = User(name=user_name)
        result = await db_ops.create_one(user)
        assert isinstance(result, User)
        user = select(User).where(User.name == user_name)
        data = await db_ops.read_one_record(user)
        assert isinstance(data, User)
        # assert data is not None

    @pytest.mark.asyncio
    async def test_read_one_record_none(self, db_ops):
        user_name = f"Mike{secrets.token_hex(10)}"

        user = select(User).where(User.name == user_name)
        data = await db_ops.read_one_record(user)
        # assert data is none
        assert data is None

    @pytest.mark.asyncio
    async def test_delete_many(self, db_ops):
        import secrets

        # db_ops is already awaited by pytest, so you can use it directly
        users = [User(name=f"User{i}-{secrets.token_hex(2)}") for i in range(100)]
        result = await db_ops.create_many(users)
        assert len(result) == 100
        # get all pkids from results
        pkids = [user.pkid for user in result]
        assert len(pkids) == 100
        # delete all users
        result = await db_ops.delete_many(
            table=User, id_column_name="pkid", id_values=pkids
        )
        # assert isinstance(result, int)
        assert result == 100

    @pytest.mark.asyncio
    async def test_delete_many_exception(self, db_ops):
        import secrets

        # db_ops is already awaited by pytest, so you can use it directly
        users = [User(name=f"User{i}-{secrets.token_hex(2)}") for i in range(10)]
        result = await db_ops.create_many(users)
        assert len(result) == 10
        # get all pkids from results
        pkids = [user.pkid for user in result]
        assert len(pkids) == 10
        result = await db_ops.delete_many(
            table=User, id_column_name=secrets.token_hex(4), id_values=pkids
        )
        # assert result contains "error"
        assert "error" in result

    @pytest.fixture(scope="class", autouse=True)
    async def setup_database(self):
        await async_db.create_tables()
        yield
        await async_db.drop_tables()

    @pytest.fixture(scope="function", autouse=True)
    async def setup_teardown(self):
        # Clean the database before each test
        await db_ops.execute_one(delete(User))
        yield
        # Clean the database after each test
        await db_ops.execute_one(delete(User))

    @pytest.mark.asyncio
    async def test_execute_one_insert(self):
        query = insert(User).values(name='Test User')
        result = await db_ops.execute_one(query)
        assert result == "complete"
        r_query = select(User).where(User.name == 'Test User')
        user = await db_ops.read_one_record(query=r_query)
        assert user.name == 'Test User'

    @pytest.mark.asyncio
    async def test_execute_many_insert(self):
        queries = [
            (insert(User), {'name': f'User {i}'}) for i in range(1, 6)
        ]
        result = await db_ops.execute_many(queries)
        assert result == "complete"
        r_query = select(User)
        users = await db_ops.read_query(query=r_query)
        assert len(users) >= 5

    @pytest.mark.asyncio
    async def test_execute_one_delete(self):
        query = insert(User).values(name='Test User')
        await db_ops.execute_one(query)
        query = delete(User).where(User.name == 'Test User')
        result = await db_ops.execute_one(query)
        assert result == "complete"
        r_query = select(User).where(User.name == 'Test User')
        user = await db_ops.read_one_record(query=r_query)
        assert user is None

    @pytest.mark.asyncio
    async def test_execute_many_delete(self):
        # Insert users to delete
        queries = [
            (insert(User), {'name': f'User {i}'}) for i in range(1, 6)
        ]
        await db_ops.execute_many(queries)
        # Fetch all users
        r_query = select(User)
        users = await db_ops.read_query(query=r_query)
        # Create delete queries based on pkid
        user_pkids = [user.pkid for user in users]
        queries = [
            (delete(User).where(User.pkid == pkid), None) for pkid in user_pkids
        ]
        result = await db_ops.execute_many(queries)
        assert result == "complete"
        # Verify all users are deleted
        users = await db_ops.read_query(query=r_query)
        assert len(users) == 0
