# -*- coding: utf-8 -*-
"""
This module provides functionality to import and validate SQLAlchemy components, ensuring compatibility with the required version.

The `import_sqlalchemy` function is the primary function in this module. It imports various components from SQLAlchemy, checks the version of SQLAlchemy, and raises an ImportError if the version is below the minimum required version.

Usage example:
    ```python
    from import_sqlalchemy import import_sqlalchemy

    sqlalchemy_components = import_sqlalchemy()
    sqlalchemy, MetaData, create_engine, text, Column, DateTime, String, IntegrityError, SQLAlchemyError, AsyncSession = sqlalchemy_components

    # Example usage of imported components
    engine = create_engine('sqlite:///example.db')
    metadata = MetaData()
    ```

Author(s):
    Mike Ryan

Date Created:
    2024/05/16
Date Updated:
    2024/07/26
"""
from typing import Tuple

from loguru import logger
from packaging import version as packaging_version

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
            - create_engine: The create_engine function from SQLAlchemy.
            - text: The text function from SQLAlchemy.
            - Column: The Column class from SQLAlchemy.
            - DateTime: The DateTime class from SQLAlchemy.
            - String: The String class from SQLAlchemy.
            - IntegrityError: The IntegrityError exception from SQLAlchemy.
            - SQLAlchemyError: The SQLAlchemyError exception from SQLAlchemy.
            - AsyncSession: The AsyncSession class from SQLAlchemy.

    Raises:
        ImportError: If SQLAlchemy is not installed or the version is below the minimum required version.

    Example:
        ```python
        from import_sqlalchemy import import_sqlalchemy

        sqlalchemy_components = import_sqlalchemy()
        sqlalchemy, MetaData, create_engine, text, Column, DateTime, String, IntegrityError, SQLAlchemyError, AsyncSession = sqlalchemy_components

        # Example usage of imported components
        engine = create_engine('sqlite:///example.db')
        metadata = MetaData()
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
