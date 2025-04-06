# -*- coding: utf-8 -*-
"""
This module provides functionality to import and validate SQLAlchemy components, ensuring compatibility with the required version.

The `import_sqlalchemy` function is the primary function in this module. It imports various components from SQLAlchemy, checks the version of SQLAlchemy, and raises an ImportError if the version is below the minimum required version.

Usage example:
    ```python
    from dsg_lib.async_database_functions.__import_sqlalchemy import import_sqlalchemy

    (
        sqlalchemy, MetaData, create_engine, text, IntegrityError, SQLAlchemyError,
        AsyncSession, create_async_engine, select, declarative_base, sessionmaker,
        Column, DateTime, String, func, NoResultFound,
    ) = import_sqlalchemy()

    # Synchronous example
    engine = create_engine('sqlite:///example.db')
    metadata = MetaData()

    # Asynchronous example
    async_engine = create_async_engine('sqlite+aiosqlite:///example.db')
    async_session = AsyncSession(async_engine)
    ```

Author(s):
    Mike Ryan

Date Created:
    2024/05/16
Date Updated:
    2025/02/15 - docstring and comments updated
"""
from typing import Tuple

from packaging import version as packaging_version

# from loguru import logger
# import logging as logger
from .. import LOGGER as logger

# Importing AsyncDatabase class from local module async_database


def import_sqlalchemy() -> Tuple:
    """
    Imports and returns SQLAlchemy components.

    This function attempts to import SQLAlchemy and its components. It checks the version of SQLAlchemy
    and raises an ImportError if the version is less than the minimum required version.

    Returns:
        Tuple: A tuple containing the following SQLAlchemy components:
            - sqlalchemy: The SQLAlchemy module.
            - MetaData: The MetaData class from SQLAlchemy.
            - create_engine: The function to create a synchronous engine.
            - text: The function that creates SQL text expressions.
            - IntegrityError: The exception raised on integrity constraint violations.
            - SQLAlchemyError: The base exception class for SQLAlchemy errors.
            - AsyncSession: The class for managing asynchronous database sessions.
            - create_async_engine: The function to create an asynchronous engine.
            - select: The future select function for query construction.
            - declarative_base: The factory function for creating a declarative base class.
            - sessionmaker: The configurable session factory.
            - Column: The class used to define a table column.
            - DateTime: The type used for temporal column definitions.
            - String: The type used for textual column definitions.
            - func: A namespace for SQL functions.
            - NoResultFound: The exception raised when a query returns no result.

    Raises:
        ImportError: If SQLAlchemy is not installed or if its version is below the minimum required version.

    Example:
        ```python
        from dsg_lib.async_database_functions.__import_sqlalchemy import import_sqlalchemy

        (
            sqlalchemy, MetaData, create_engine, text, IntegrityError, SQLAlchemyError,
            AsyncSession, create_async_engine, select, declarative_base, sessionmaker,
            Column, DateTime, String, func, NoResultFound,
        ) = import_sqlalchemy()

        # Synchronous engine usage example
        engine = create_engine('sqlite:///example.db')
        metadata = MetaData()

        # Example usage of asynchronous components
        async_engine = create_async_engine('sqlite+aiosqlite:///example.db')
        async_session = AsyncSession(async_engine)
        ```
    """
    min_version = "2.0.0"  # Minimum required version of SQLAlchemy

    logger.info("Attempting to import SQLAlchemy...")

    try:
        # Import SQLAlchemy and its components
        import sqlalchemy
        from sqlalchemy import Column, DateTime, MetaData, String, create_engine, text
        from sqlalchemy.exc import IntegrityError, SQLAlchemyError
        from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
        from sqlalchemy.future import select
        from sqlalchemy.orm import declarative_base, sessionmaker
        from sqlalchemy.orm.exc import NoResultFound
        from sqlalchemy.sql import func

        logger.info("Successfully imported SQLAlchemy.")

    except ImportError:  # pragma: no cover
        # Handle the case where SQLAlchemy is not installed
        logger.error("Failed to import SQLAlchemy.")
        create_engine = text = sqlalchemy = None  # pragma: no cover

    # Check SQLAlchemy version
    if sqlalchemy is not None and packaging_version.parse(
        sqlalchemy.__version__
    ) < packaging_version.parse(min_version):
        # If the installed version is less than the minimum required version, raise an error
        logger.error(
            f"SQLAlchemy version >= {min_version} required, run `pip install --upgrade sqlalchemy`"
        )
        raise ImportError(
            f"SQLAlchemy version >= {min_version} required, run `pip install --upgrade sqlalchemy`"
        )  # pragma: no cover

    logger.info("Returning SQLAlchemy components.")

    # Return the imported SQLAlchemy components
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
        Column,
        DateTime,
        String,
        func,
        NoResultFound,
    )


# Call the import_sqlalchemy function and unpack its return value
# into several variables. Each variable corresponds to a component
# of SQLAlchemy that we want to use in our code.

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
