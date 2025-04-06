# -*- coding: utf-8 -*-
"""
async_database.py

This module provides classes for managing asynchronous database operations using
SQLAlchemy and asyncio.

Classes:
    - DBConfig: Initializes and manages the database configuration including the
      creation of the SQLAlchemy engine and MetaData instance.
    - AsyncDatabase: Leverages a DBConfig instance to perform asynchronous
      database operations such as obtaining sessions, creating tables, and disconnecting
      from the database.

Logging is performed using the logger from dsg_lib.common_functions.

Example:
    ```python
    from dsg_lib.async_database_functions import (
        async_database,
        base_schema,
        database_config,
        database_operations,
    )

    # Define database configuration
    config = {
        "database_uri": "sqlite+aiosqlite:///:memory:?cache=shared",
        "echo": False,
        "future": True,
        "pool_recycle": 3600,
    }

    # Create the configuration instance
    db_config = database_config.DBConfig(config)

    # Instantiate AsyncDatabase with the given configuration
    async_db = async_database.AsyncDatabase(db_config)

    # Optionally, create a DatabaseOperations instance
    db_ops = database_operations.DatabaseOperations(async_db)
    ```

Author:
    Mike Ryan

Date Created:
    2024/05/16

Date Updated:
    2025/02/15 - docstring and comments updated

License:
    MIT
"""

# from loguru import logger
# import logging as logger
from .. import LOGGER as logger
from .database_config import BASE, DBConfig


class AsyncDatabase:
    """
    Manages asynchronous database operations.

    This class provides methods to acquire database sessions, create tables asynchronously,
    and disconnect the database engine safely.

    Attributes
    ----------
    db_config : DBConfig
        An instance of DBConfig containing the database configuration such as the engine.
    Base : Base
        The declarative base model used by SQLAlchemy to define database models.

    Methods
    -------
    get_db_session():
        Returns a context manager that yields a new asynchronous database session.
    create_tables():
        Asynchronously creates all tables as defined in the metadata.
    disconnect():
        Asynchronously disconnects the database engine.
    """

    def __init__(self, db_config: DBConfig):
        """
        Initialize AsyncDatabase with a database configuration.

        Parameters
        ----------
        db_config : DBConfig
            An instance of DBConfig containing the necessary database configurations.
        """
        self.db_config = db_config
        self.Base = BASE
        logger.debug("AsyncDatabase initialized")

    def get_db_session(self):
        """
        Obtain a new asynchronous database session.

        Returns
        -------
        contextlib._GeneratorContextManager
            A context manager that yields a new database session.
        """
        logger.debug("Getting database session")
        return self.db_config.get_db_session()

    async def create_tables(self):
        """
        Asynchronously create all tables defined in the metadata.

        This method binds the engine to the Base metadata and runs the table creation
        in a synchronous manner within an asynchronous transaction.

        Raises
        ------
        Exception
            Propagates any exceptions encountered during table creation.
        """
        logger.debug("Creating tables")
        try:
            # Bind the engine to the Base metadata
            self.Base.metadata.bind = self.db_config.engine

            # Begin an asynchronous transaction and create tables synchronously
            async with self.db_config.engine.begin() as conn:
                await conn.run_sync(self.Base.metadata.create_all)
            logger.info("Tables created successfully")
        except Exception as ex:  # pragma: no cover
            logger.error(f"Error creating tables: {ex}")  # pragma: no cover
            raise  # pragma: no cover

    async def disconnect(self):  # pragma: no cover
        """
        Asynchronously disconnect the database engine.

        Closes all connections and disposes of the engine resources.

        Raises
        ------
        Exception
            Propagates any exceptions encountered during disconnection.
        """
        logger.debug("Disconnecting from database")
        try:
            await self.db_config.engine.dispose()
            logger.info("Disconnected from database")
        except Exception as ex:  # pragma: no cover
            logger.error(f"Error disconnecting from database: {ex}")  # pragma: no cover
            raise  # pragma: no cover
