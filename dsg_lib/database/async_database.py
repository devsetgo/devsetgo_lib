# -*- coding: utf-8 -*-
"""async_database.py.

This module contains several classes that handle database operations in an asynchronous manner using SQLAlchemy and asyncio.

Classes:
    - DBConfig: Manages the database configuration.
    - AsyncDatabase: Manages the asynchronous database operations.
    - DatabaseOperationException: A custom exception class for handling database operation errors.
    - DatabaseOperations: Manages the database operations.

The DBConfig class initializes the database configuration and creates a SQLAlchemy engine and a MetaData instance.

The AsyncDatabase class uses an instance of DBConfig to perform asynchronous database operations. It provides methods to get a database session and to create tables in the database.

The DatabaseOperationException class is a custom exception class that is used to handle errors that occur during database operations. It includes the HTTP status code and a detailed message about the error.

The DatabaseOperations class uses an instance of AsyncDatabase to perform various database operations such as executing count queries, fetch queries, and adding records to the database. It handles errors by raising a DatabaseOperationException with the appropriate status code and detail message.

This module uses the logger from the devsetgo_toolkit for logging.
"""

# Importing necessary modules and functions

from sqlalchemy.orm import declarative_base

from ..logger import logger
from .database_config import DBConfig

# Creating a base class for declarative database models
Base = declarative_base()


class AsyncDatabase:
    """
    A class used to manage the asynchronous database operations.

    ...

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
        db_config (DBConfig): An instance of DBConfig class containing the database configuration.

        Returns: None
        """
        self.db_config = db_config
        self.Base = Base
        # Bind the engine to the metadata of the base class,
        # so that declaratives can be accessed through a DBSession instance
        self.Base.metadata.bind = self.db_config.engine
        logger.debug("AsyncDatabase initialized")

    def get_db_session(self):
        """This method returns a context manager that provides a new database
        session.

        Parameters: None

        Returns:
        contextlib._GeneratorContextManager: A context manager that provides a new database session.
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
            # Begin a new transaction
            async with self.db_config.engine.begin() as conn:
                # Run a function in a synchronous manner
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Tables created successfully")
        except Exception as e:  # pragma: no cover
            # Log the error and raise it
            logger.error(f"Error creating tables: {e}")  # pragma: no cover
            raise  # pragma: no cover
