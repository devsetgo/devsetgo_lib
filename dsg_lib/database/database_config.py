# -*- coding: utf-8 -*-
"""
database_config.py
------------------

This module provides classes and functions for managing asynchronous database operations using SQLAlchemy and asyncio.

The main classes are DBConfig, which manages the database configuration and creates a SQLAlchemy engine and a MetaData instance, and AsyncDatabase, which uses an instance of DBConfig to perform asynchronous database operations.

The module also provides a function, import_sqlalchemy, which tries to import SQLAlchemy and its components, and raises an ImportError if SQLAlchemy is not installed or if the installed version is not compatible.

The module uses the logger from the `dsg_lib` for logging, and the `time` module for working with times. It also uses the `contextlib` module for creating context managers, and the `typing` module for type hinting.

The `BASE` variable is a base class for declarative database models. It is created using the `declarative_base` function from `sqlalchemy.orm`.

This module is part of the `dsg_lib` package, which provides utilities for working with databases in Python.
"""

import time  # Importing time module to work with times
from contextlib import (
    asynccontextmanager,  # Importing asynccontextmanager from contextlib for creating context managers
)
from typing import Dict  # Importing Dict and List from typing for type hinting

from packaging import version as packaging_version

# import logging as logger
from ..logger import logger


def import_sqlalchemy():
    # Try to import SQLAlchemy, handle ImportError if SQLAlchemy is not installed
    try:
        import sqlalchemy
        from sqlalchemy import MetaData, create_engine, text
        from sqlalchemy.exc import IntegrityError, SQLAlchemyError
        from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
        from sqlalchemy.future import select
        from sqlalchemy.orm import declarative_base, sessionmaker

    except ImportError:  # pragma: no cover
        create_engine = text = sqlalchemy = None  # pragma: no cover

    # Check SQLAlchemy version
    min_version = "2.0.0"  # replace with your minimum required version
    if sqlalchemy is not None and packaging_version.parse(
        sqlalchemy.__version__
    ) < packaging_version.parse(min_version):
        raise ImportError(
            f"SQLAlchemy version >= {min_version} required, run `pip install --upgrade sqlalchemy`"
        )  # pragma: no cover

    return (
        sqlalchemy,
        MetaData,
        create_engine,
        text,
        IntegrityError,
        SQLAlchemyError,
        AsyncSession,
        create_async_engine,
        select,
        declarative_base,
        sessionmaker,
    )


# Call the function at the module level
(
    sqlalchemy,
    MetaData,
    create_engine,
    text,
    IntegrityError,
    SQLAlchemyError,
    AsyncSession,
    create_async_engine,
    select,
    declarative_base,
    sessionmaker,
) = import_sqlalchemy()

# Now you can use declarative_base at the module level
BASE = declarative_base()


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
    To Be Tested [MySQL, Oracle, MSSQL] and should be considered experimental
    -------
    Option          SQLite  PostgreSQL  MySQL   Oracle  MSSQL
    echo                Yes         Yes         Yes     Yes     Yes
    future              Yes         Yes         Yes     Yes     Yes
    pool_pre_ping       Yes         Yes         Yes     Yes     Yes
    pool_size           No          Yes         Yes     Yes     Yes
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
