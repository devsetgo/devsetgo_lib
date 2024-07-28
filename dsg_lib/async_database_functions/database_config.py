# -*- coding: utf-8 -*-
"""
This module provides classes and functions for managing asynchronous database
operations using SQLAlchemy and asyncio.

The main classes are DBConfig, which manages the database configuration and
creates a SQLAlchemy engine and a MetaData instance, and AsyncDatabase, which
uses an instance of DBConfig to perform asynchronous database operations.

The module also provides a function, import_sqlalchemy, which tries to import
SQLAlchemy and its components, and raises an ImportError if SQLAlchemy is not
installed or if the installed version is not compatible.

The module uses the logger from the `dsg_lib` for logging, and the `time` module
for working with times. It also uses the `contextlib` module for creating
context managers, and the `typing` module for type hinting.

The `BASE` variable is a base class for declarative database models. It is
created using the `declarative_base` function from `sqlalchemy.orm`.

This module is part of the `dsg_lib` package, which provides utilities for
working with databases in Python.

Example:
```python

from dsg_lib.async_database_functions import database_config

# Define your database configuration config = {
    "database_uri": "postgresql+asyncpg://user:password@localhost/dbname",
    "echo": True, "future": True, "pool_pre_ping": True, "pool_size": 5,
    "max_overflow": 10, "pool_recycle": 3600, "pool_timeout": 30,
}

# Create a DBConfig instance db_config = database_config.DBConfig(config)

# Use the DBConfig instance to get a database session async with
db_config.get_db_session() as session:
    # Perform your database operations here pass
```

Author: Mike Ryan
Date: 2024/05/16
License: MIT
"""
from contextlib import asynccontextmanager
from typing import Dict

from loguru import logger

from .__import_sqlalchemy import import_sqlalchemy

(
    sqlalchemy,  # The SQLAlchemy module
    MetaData,  # The MetaData class from SQLAlchemy
    create_engine,  # The create_engine function from SQLAlchemy
    text,  # The text function from SQLAlchemy
    IntegrityError,  # The IntegrityError exception from SQLAlchemy
    SQLAlchemyError,  # The SQLAlchemyError exception from SQLAlchemy
    AsyncSession,  # The AsyncSession class from SQLAlchemy
    create_async_engine,  # The create_async_engine function from SQLAlchemy
    select,  # The select function from SQLAlchemy
    declarative_base,  # The declarative_base function from SQLAlchemy
    sessionmaker,  # The sessionmaker function from SQLAlchemy
    Column,  # The Column class from SQLAlchemy
    DateTime,  # The DateTime class from SQLAlchemy
    String,  # The String class from SQLAlchemy
    func,  # The func object from SQLAlchemy
    NoResultFound,  # The NoResultFound exception from SQLAlchemy
) = (
    import_sqlalchemy()
)  # Call the function that imports SQLAlchemy and checks its version


# Now you can use declarative_base at the module level
BASE = declarative_base()


class DBConfig:
    """
    A class used to manage the database configuration and create a SQLAlchemy
    engine.

    Attributes:
        config (dict): A dictionary containing the database configuration
        parameters. engine (Engine): The SQLAlchemy engine created with the
        database URI from the config. metadata (MetaData): The SQLAlchemy
        MetaData instance.


    Create Engine Support Functions by Database Type Confirmed by testing
    [SQLITE, PostrgeSQL] To Be Tested [MySQL, Oracle, MSSQL] and should be
    considered experimental ------- Option          SQLite  PostgreSQL  MySQL
    Oracle  MSSQL echo                Yes         Yes         Yes     Yes
    Yes future              Yes         Yes         Yes     Yes     Yes
    pool_pre_ping       Yes         Yes         Yes     Yes     Yes pool_size
    No          Yes         Yes     Yes     Yes max_overflow        No
    Yes         Yes     Yes     Yes pool_recycle        Yes         Yes
    Yes     Yes     Yes pool_timeout        No          Yes         Yes     Yes
    Yes

    Example:
    ```python

    from dsg_lib.async_database_functions import database_config

    # Define your database configuration config = {
        "database_uri": "postgresql+asyncpg://user:password@localhost/dbname",
        "echo": True, "future": True, "pool_pre_ping": True, "pool_size": 5,
        "max_overflow": 10, "pool_recycle": 3600, "pool_timeout": 30,
    }

    # Create a DBConfig instance db_config = database_config.DBConfig(config)

    # Use the DBConfig instance to get a database session async with
    db_config.get_db_session() as session:
        # Perform your database operations here pass
    ```

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
        """
        Initializes the DBConfig instance with the given database configuration.

        The configuration should be a dictionary with the following keys: -
        "database_uri": The URI for the database. - "echo": If True, the engine
        will log all statements as well as a `repr()` of their parameter lists
        to the engines logger, which defaults to sys.stdout. - "future": If
        True, use the future version of SQLAlchemy, which supports asyncio. -
        "pool_pre_ping": If True, the pool will test the connection for liveness
        upon each checkout. - "pool_size": The size of the connection pool to be
        maintained. - "max_overflow": The number of connections that can be
        opened above the `pool_size` setting, when all other connections are in
        use. - "pool_recycle": The number of seconds after which a connection is
        automatically recycled. This is required for MySQL, which removes
        connections after 8 hours idle by default. - "pool_timeout": The number
        of seconds to wait before giving up on getting a connection from the
        pool.

        Args:
            config (Dict): A dictionary containing the database configuration
            parameters.

        Raises:
            Exception: If there are unsupported parameters for the database
            engine type.

        Example:
        ```python

        from dsg_lib.async_database_functions import database_config

        # Define your database configuration config = {
            "database_uri":
            "postgresql+asyncpg://user:password@localhost/dbname", "echo": True,
            "future": True, "pool_pre_ping": True, "pool_size": 5,
            "max_overflow": 10, "pool_recycle": 3600, "pool_timeout": 30,
        }

        # Create a DBConfig instance db_config =
        database_config.DBConfig(config)
        ```
        """
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
        """
        This method returns a context manager that provides a new database
        session.

        The session is created using the SQLAlchemy engine from the DBConfig
        instance, and it does not expire on commit. The session is of type
        AsyncSession.

        This method should be used with the `async with` statement.

        Yields:
            AsyncSession: A new SQLAlchemy asynchronous session.

        Raises:
            SQLAlchemyError: If a database error occurs.

        Example:
        ```python

        from dsg_lib.async_database_functions import database_config

        # Define your database configuration config = {
            "database_uri":
            "postgresql+asyncpg://user:password@localhost/dbname", "echo": True,
            "future": True, "pool_pre_ping": True, "pool_size": 5,
            "max_overflow": 10, "pool_recycle": 3600, "pool_timeout": 30,
        }

        # Create a DBConfig instance db_config =
        database_config.DBConfig(config)

        # Use the DBConfig instance to get a database session async with
        db_config.get_db_session() as session:
            # Perform your database operations here pass
        ```
        """
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
