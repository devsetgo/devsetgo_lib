# -*- coding: utf-8 -*-
"""async_database.py.

This module provides classes for managing asynchronous database operations using
SQLAlchemy and asyncio.

Classes:
    - DBConfig: Manages the database configuration.
    - AsyncDatabase: Manages the asynchronous database operations.

The DBConfig class initializes the database configuration and creates a
SQLAlchemy engine and a MetaData instance.

The AsyncDatabase class uses an instance of DBConfig to perform asynchronous
database operations. It provides methods to get a database session and to create
tables in the database.

This module uses the logger from the dsg_lib.common_functions for logging.

Example:
```python
from dsg_lib.async_database_functions import (
    async_database,
    base_schema,
    database_config,
    database_operations,
)

# Create a DBConfig instance
config = {
    "database_uri": "sqlite+aiosqlite:///:memory:?cache=shared",
    "echo": False,
    "future": True,
    "pool_recycle": 3600,
}

# create database configuration
db_config = database_config.DBConfig(config)

# Create an AsyncDatabase instance
async_db = async_database.AsyncDatabase(db_config)

# Create a DatabaseOperations instance
db_ops = database_operations.DatabaseOperations(async_db)
```

Author: Mike Ryan
Date: 2024/05/16
License: MIT
"""


from loguru import logger

from .database_config import BASE, DBConfig


class AsyncDatabase:
    """
    A class used to manage the asynchronous database operations.

    Attributes
    ----------
    db_config : DBConfig
        an instance of DBConfig class containing the database configuration
    Base : Base
        the declarative base model for SQLAlchemy

    Methods
    -------
    get_db_session():
        Returns a context manager that provides a new database session.
    create_tables():
        Asynchronously creates all tables in the database.
    """

    def __init__(self, db_config: DBConfig):
        """Initialize the AsyncDatabase class with an instance of DBConfig.

        Parameters:
        db_config (DBConfig): An instance of DBConfig class containing the
        database configuration.

        Returns: None
        """
        self.db_config = db_config
        self.Base = BASE
        logger.debug("AsyncDatabase initialized")

    def get_db_session(self):
        """This method returns a context manager that provides a new database
        session.

        Parameters: None

        Returns: contextlib._GeneratorContextManager: A context manager that
        provides a new database session.
        """
        logger.debug("Getting database session")
        return self.db_config.get_db_session()

    async def create_tables(self):
        """This method asynchronously creates all tables in the database.

        Parameters: None

        Returns: None
        """
        logger.debug("Creating tables")
        try:
            # Bind the engine to the metadata of the base class
            self.Base.metadata.bind = self.db_config.engine

            # Begin a new transaction
            async with self.db_config.engine.begin() as conn:
                # Run a function in a synchronous manner
                await conn.run_sync(self.Base.metadata.create_all)
            logger.info("Tables created successfully")
        except Exception as ex:  # pragma: no cover
            # Log the error and raise it
            logger.error(f"Error creating tables: {ex}")  # pragma: no cover
            raise  # pragma: no cover

    async def disconnect(self): # pragma: no cover
        """
        This method asynchronously disconnects the database engine.

        Parameters: None

        Returns: None
        """
        logger.debug("Disconnecting from database")
        try:
            await self.db_config.engine.dispose()
            logger.info("Disconnected from database")
        except Exception as ex:  # pragma: no cover
            logger.error(f"Error disconnecting from database: {ex}")  # pragma: no cover
            raise  # pragma: no cover
