# Asynchronous Database Module

This module, `async_database.py`, is designed to manage asynchronous database operations using SQLAlchemy and asyncio.

## Purpose

The purpose of this module is to allow your application to set up its database connections in a non-blocking manner. This is particularly useful in web applications where you want to start serving requests as soon as possible, even if the database setup is still ongoing.

The module provides two main classes:

- `DBConfig`: Manages the database configuration and creates a SQLAlchemy engine and a MetaData instance.
- `AsyncDatabase`: Manages the asynchronous database operations. It uses an instance of `DBConfig` to perform these operations.

## How to Use

To use this module, you need to create an instance of `DBConfig` with your database configuration, and then create an instance of `AsyncDatabase` with the `DBConfig` instance. Here's an example:

```python
from async_database import DBConfig, AsyncDatabase

# Create a DBConfig instance
db_config = DBConfig(database_url="sqlite:///./test.db")

# Create an AsyncDatabase instance
async_db = AsyncDatabase(db_config=db_config)
```

You can then use the `get_db_session` method of `AsyncDatabase` to get a new database session, and the `create_tables` method to create all tables in the database:

```python
# Get a new database session
with async_db.get_db_session() as session:
    # Perform database operations with the session...

# Asynchronously create all tables in the database
await async_db.create_tables()
```

## Dependencies

This module depends on several Python packages, including:

- `sqlalchemy` for the database operations.
- `asyncio` for the asynchronous operations.
- `logger` from the `dsg_lib` package for logging.

## Note

This module requires careful error handling to ensure that database errors don't crash the application. It also requires a mechanism for checking the status of the database setup, and for waiting for the setup to complete when necessary.