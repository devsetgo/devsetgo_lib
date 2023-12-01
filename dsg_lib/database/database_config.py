# -*- coding: utf-8 -*-
"""database_config.py.

This module is designed to handle asynchronous database operations using SQLAlchemy and asyncio. It contains several classes that each play a specific role in managing and interacting with the database.

Classes:
    - DBConfig: This class is responsible for managing the database configuration. It initializes the database configuration and creates a SQLAlchemy engine and a MetaData instance. The configuration is passed as a dictionary and includes parameters such as the database URI, pool size, and timeout settings. The class also provides a method to get a new database session.

    - AsyncDatabase: This class uses an instance of DBConfig to perform asynchronous database operations. It provides methods to get a database session and to create tables in the database.

    - DatabaseOperationException: This is a custom exception class that is used to handle errors that occur during database operations. It includes the HTTP status code and a detailed message about the error.

    - DatabaseOperations: This class uses an instance of AsyncDatabase to perform various database operations such as executing count queries, fetch queries, and adding records to the database. It handles errors by raising a DatabaseOperationException with the appropriate status code and detail message.

The module uses the logger from the devsetgo_toolkit for logging. The logging helps in tracking the flow of operations and in debugging by providing useful information about the operations being performed and any errors that occur.

The module also uses the time module to work with times, the contextlib module for creating context managers, and the typing module for type hinting. It uses several components from the sqlalchemy package for database operations and error handling.

The Base variable is a base class for declarative database models. It is created using the declarative_base function from sqlalchemy.orm.

The SUPPORTED_PARAMETERS constant in the DBConfig class is a dictionary that specifies the supported parameters for different types of databases. This helps in validating the configuration parameters passed to the DBConfig class.

The module is designed to be flexible and can be extended to support additional database types and operations.
"""

import time  # Importing time module to work with times
from contextlib import (  # Importing asynccontextmanager from contextlib for creating context managers
    asynccontextmanager,
)
from typing import Dict, List  # Importing Dict and List from typing for type hinting

from sqlalchemy import (  # Importing MetaData and func from sqlalchemy for database operations
    MetaData,
    func,
)
from sqlalchemy.exc import (  # Importing specific exceptions from sqlalchemy for error handling
    IntegrityError,
    SQLAlchemyError,
)
from sqlalchemy.ext.asyncio import (  # Importing AsyncSession and create_async_engine from sqlalchemy for asynchronous database operations
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.future import (  # Importing select from sqlalchemy for making select queries
    select,
)
from sqlalchemy.orm import (  # Importing declarative_base and sessionmaker from sqlalchemy for ORM operations
    declarative_base,
    sessionmaker,
)

# import logging as logger
from ..logger import logger

Base = declarative_base()  # Creating a base class for declarative database models


class DBConfig:
    """A class used to manage the database configuration.

    Attributes
    ----------
    config : Dict
        a dictionary containing the database configuration. Example:

        config = {
            "database_uri": "postgresql+asyncpg://user:password@localhost/dbname",
            "echo": True,
            "future": True,
            "pool_pre_ping": True,
            "pool_size": 5,
            "max_overflow": 10,
            "pool_recycle": 3600,
            "pool_timeout": 30,
        }

        This config dictionary can be passed to the DBConfig class like this:

        db_config = DBConfig(config)

        This will create a new DBConfig instance with a SQLAlchemy engine configured according to the parameters in the config dictionary.

    engine : Engine
        the SQLAlchemy engine created with the database URI from the config
    metadata : MetaData
    the SQLAlchemy MetaData instance
    Methods
    -------
    get_db_session():
        Returns a context manager that provides a new database session.

    Create Engine Support Functions by Database Type
    Confirmed by testing [SQLITE, PostrgeSQL]
    To Be Tested [MySQL, Oracle, MSSQL]
    -------
    Option          SQLite  PostgreSQL  MySQL   Oracle  MSSQL
    echo                Yes         Yes         Yes     Yes     Yes
    future              Yes         Yes         Yes     Yes     Yes
    pool_pre_ping       Yes         Yes         Yes     Yes     Yes
    pool_size       No      Yes         Yes     Yes     Yes
    max_overflow        No          Yes         Yes     Yes     Yes
    pool_recycle        Yes         Yes         Yes     Yes     Yes
    pool_timeout        No          Yes         Yes     Yes     Yes
    """

    SUPPORTED_PARAMETERS = {
        "sqlite": {"echo", "future", "pool_recycle"},
        "postgresql": {
            "echo",
            "future",
            "pool_pre_ping",
            "pool_size",
            "max_overflow",
            "pool_recycle",
            "pool_timeout",
        },
        # Add other engines here...
    }

    def __init__(self, config: Dict):
        self.config = config
        engine_type = self.config["database_uri"].split("+")[0]
        supported_parameters = self.SUPPORTED_PARAMETERS.get(engine_type, set())
        unsupported_parameters = (
            set(config.keys()) - supported_parameters - {"database_uri"}
        )
        if unsupported_parameters:
            error_message = (
                f"Unsupported parameters for {engine_type}: {unsupported_parameters}"
            )
            logger.error(error_message)
            raise Exception(error_message)

        engine_parameters = {
            param: self.config.get(param)
            for param in supported_parameters
            if self.config.get(param) is not None
        }
        self.engine = create_async_engine(
            self.config["database_uri"], **engine_parameters
        )
        self.metadata = MetaData()

    @asynccontextmanager
    async def get_db_session(self):
        # This method returns a context manager that provides a new database session
        logger.debug("Creating new database session")
        try:
            # Create a new database session
            async with sessionmaker(
                self.engine, expire_on_commit=False, class_=AsyncSession
            )() as session:
                # Yield the session to the context manager
                yield session
        except SQLAlchemyError as e:  # pragma: no cover
            # Log the error and raise it
            logger.error(f"Database error occurred: {str(e)}")  # pragma: no cover
            raise  # pragma: no cover
        finally:  # pragma: no cover
            # Log the end of the database session
            logger.debug("Database session ended")  # pragma: no cover
