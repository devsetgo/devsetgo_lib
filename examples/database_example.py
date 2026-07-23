# -*- coding: utf-8 -*-
"""
# Database Example Module

Demonstrates `dsg_lib.async_database_functions`, the async SQLAlchemy toolkit
made up of four pieces that are normally wired together in this order:

1. `database_config.DBConfig` -- turns a plain config dict into a SQLAlchemy
   async engine + session factory.
2. `async_database.AsyncDatabase` -- wraps a `DBConfig` and adds
   `create_tables()` / `disconnect()` and the shared declarative `Base`.
3. `base_schema.SchemaBaseSQLite` -- a mixin that gives every model a
   `pkid`/`date_created`/`date_updated` column for free (dialect-specific
   siblings exist for Postgres, MySQL, Oracle, MSSQL, Firebird, Sybase, and
   CockroachDB).
4. `database_operations.DatabaseOperations` -- the query surface used at
   runtime: `execute_one` / `execute_many` for writes, `read_query` /
   `read_one_record` / `read_multi_query` / `count_query` / `paginate_query`
   for reads, plus introspection (`get_table_names`, `get_columns_details`,
   `get_primary_keys`).

This example uses an in-memory SQLite database (`sqlite+aiosqlite:///:memory:`)
so it runs standalone with no external services, but every call shown here
works unchanged against Postgres/MySQL/MSSQL/Oracle -- only the
`database_uri` and the `SchemaBase*` mixin change.

## Functions

### `build_database() -> AsyncDatabase`
Builds the `DBConfig` -> `AsyncDatabase` pair and creates the tables for the
`User` model defined in this module.

### `insert_users(db_ops, names) -> dict`
Inserts several rows in one transaction via `execute_many`.

### `read_examples(db_ops) -> dict`
Runs `read_query`, `read_one_record`, `read_multi_query`, `count_query`, and
`paginate_query` against the seeded data.

### `update_and_delete(db_ops, user_id) -> dict`
Runs an `execute_one` UPDATE and an `execute_one` DELETE against a single row.

### `inspect_schema(db_ops) -> dict`
Runs the introspection helpers: `get_table_names`, `get_columns_details`,
`get_primary_keys`.

## Usage

Run the module directly to build the database, seed it, exercise every read
and write method, inspect the schema, and disconnect.

## Example Execution

```bash
python database_example.py
```
## License
This module is licensed under the MIT License.
"""
import asyncio
from typing import Any, Dict, List

from sqlalchemy import Column, String, delete, insert, select, update

from dsg_lib.async_database_functions import (
    async_database,
    base_schema,
    database_config,
    database_operations,
)
from dsg_lib.async_database_functions.database_config import BASE


class User(base_schema.SchemaBaseSQLite, BASE):
    """A minimal model: `pkid`/`date_created`/`date_updated` come from the mixin."""

    __tablename__ = "example_users"

    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=True)

    def __repr__(self) -> str:
        return f"User(name={self.name!r}, email={self.email!r})"


async def build_database() -> async_database.AsyncDatabase:
    """
    Create the engine/session factory and the `example_users` table.

    Returns:
        AsyncDatabase: A ready-to-use database wrapper.
    """
    config = {
        "database_uri": "sqlite+aiosqlite:///:memory:?cache=shared",
        "echo": False,
        "future": True,
        "pool_recycle": 3600,
    }
    db_config = database_config.DBConfig(config)
    async_db = async_database.AsyncDatabase(db_config)
    await async_db.create_tables()
    return async_db


async def insert_users(
    db_ops: database_operations.DatabaseOperations, names: List[str]
) -> Dict[str, Any]:
    """
    Insert one row per name in a single transaction using `execute_many`.

    Args:
        db_ops (DatabaseOperations): The operations instance to run queries with.
        names (List[str]): Names to insert as `User` rows.

    Returns:
        Dict[str, Any]: Per-row metadata (rowcount, inserted_primary_key) for each insert.
    """
    queries = [
        (insert(User), {"name": name, "email": f"{name.lower()}@example.com"})
        for name in names
    ]
    result = await db_ops.execute_many(queries, return_results=True)
    return {"insert_metadata": result}


async def read_examples(db_ops: database_operations.DatabaseOperations) -> Dict[str, Any]:
    """
    Demonstrate every read method against the seeded `example_users` table.

    Args:
        db_ops (DatabaseOperations): The operations instance to run queries with.

    Returns:
        Dict[str, Any]: The result of each read method, keyed by method name.
    """
    all_users = await db_ops.read_query(select(User).order_by(User.name))

    one_user = await db_ops.read_one_record(select(User).where(User.name == "Ada"))

    multi = await db_ops.read_multi_query(
        {
            "names_only": select(User.name).order_by(User.name),
            "all_columns": select(User).order_by(User.name),
        }
    )

    total = await db_ops.count_query(select(User))

    page = await db_ops.paginate_query(select(User).order_by(User.name), page=1, page_size=2)

    return {
        "read_query": all_users,
        "read_one_record": one_user,
        "read_multi_query": multi,
        "count_query": total,
        "paginate_query": page,
    }


async def update_and_delete(
    db_ops: database_operations.DatabaseOperations, name_to_update: str, name_to_delete: str
) -> Dict[str, Any]:
    """
    Update one row and delete another, both via `execute_one`.

    Args:
        db_ops (DatabaseOperations): The operations instance to run queries with.
        name_to_update (str): Existing name whose email should be changed.
        name_to_delete (str): Existing name to remove entirely.

    Returns:
        Dict[str, Any]: Metadata from the UPDATE and the DELETE.
    """
    update_query = (
        update(User).where(User.name == name_to_update).values(email="updated@example.com")
    )
    update_meta = await db_ops.execute_one(update_query, return_metadata=True)

    delete_query = delete(User).where(User.name == name_to_delete)
    delete_meta = await db_ops.execute_one(delete_query, return_metadata=True)

    return {"update": update_meta, "delete": delete_meta}


async def inspect_schema(db_ops: database_operations.DatabaseOperations) -> Dict[str, Any]:
    """
    Demonstrate the introspection helpers against the `User` model.

    Args:
        db_ops (DatabaseOperations): The operations instance to run queries with.

    Returns:
        Dict[str, Any]: Table names, column details, and primary keys.
    """
    return {
        "table_names": await db_ops.get_table_names(),
        "columns": await db_ops.get_columns_details(User),
        "primary_keys": await db_ops.get_primary_keys(User),
    }


async def main() -> None:
    print("Building database and creating tables...")
    async_db = await build_database()
    db_ops = database_operations.DatabaseOperations(async_db)

    print("\nInserting users via execute_many...")
    print(await insert_users(db_ops, ["Ada", "Grace", "Alan"]))

    print("\nRunning read examples...")
    for name, result in (await read_examples(db_ops)).items():
        print(f"  {name}: {result}")

    print("\nUpdating and deleting via execute_one...")
    print(await update_and_delete(db_ops, name_to_update="Ada", name_to_delete="Alan"))

    print("\nInspecting schema...")
    for name, result in (await inspect_schema(db_ops)).items():
        print(f"  {name}: {result}")

    print("\nDisconnecting...")
    await async_db.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
