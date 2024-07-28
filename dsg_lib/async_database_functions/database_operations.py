# -*- coding: utf-8 -*-
"""
This module provides the `DatabaseOperations` class for performing CRUD operations on a database using SQLAlchemy's asynchronous session.

The `DatabaseOperations` class includes the following methods:

    - `create_one`: Creates a single record in the database.
    - `create_many`: Creates multiple records in the database.
    - `read_one`: Reads a single record from the database.
    - `read_many`: Reads multiple records from the database.
    - `update_one`: Updates a single record in the database.
    - `update_many`: Updates multiple records in the database.
    - `delete_one`: Deletes a single record from the database.
    - `delete_many`: Deletes multiple records from the database.
    - `read_query`: Executes a fetch query on the database and returns a list of records that match the query.
    - `read_multi_query`: Executes multiple fetch queries on the database and returns a dictionary of results for each query.
    - `count_query`: Counts the number of records that match a given query.
    - `get_column_details`: Gets the details of the columns in a table.
    - `get_primary_keys`: Gets the primary keys of a table.
    - `get_table_names`: Gets the names of all tables in the database.


Each method is designed to handle errors correctly and provide a simple interface for performing database operations.

This module also imports the necessary SQLAlchemy and loguru modules, and the `AsyncDatabase` class from the local `async_database` module.

Author: Mike Ryan
Date: 2024/05/16
License: MIT
"""

import time
from typing import Dict, List, Type

from loguru import logger
from sqlalchemy import delete
from sqlalchemy.ext.declarative import DeclarativeMeta

from .__import_sqlalchemy import import_sqlalchemy
# Importing AsyncDatabase class from local module async_database
from .async_database import AsyncDatabase

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


def handle_exceptions(ex: Exception) -> Dict[str, str]:
    """
    Handles exceptions for database operations.

    This function checks the type of the exception, logs an appropriate error
    message, and returns a dictionary containing the error details.

    Args:
        ex (Exception): The exception to handle.

    Returns:
        dict: A dictionary containing the error details. The dictionary has two
        keys: 'error' and 'details'.

    Example:
    ```python
    from dsg_lib.async_database_functions import database_operations

    try:
        # Some database operation that might raise an exception pass
    except Exception as ex:
        error_details = database_operations.handle_exceptions(ex)
        print(error_details)
    ```
    """
    # Extract the error message before the SQL statement
    error_only = str(ex).split("[SQL:")[0]

    # Check the type of the exception
    if isinstance(ex, IntegrityError):
        # Log the error and return the error details
        logger.error(f"IntegrityError occurred: {ex}")
        return {"error": "IntegrityError", "details": error_only}
    elif isinstance(ex, SQLAlchemyError):
        # Log the error and return the error details
        logger.error(f"SQLAlchemyError occurred: {ex}")
        return {"error": "SQLAlchemyError", "details": error_only}
    else:
        # Log the error and return the error details
        logger.error(f"Exception occurred: {ex}")
        return {"error": "General Exception", "details": str(ex)}


class DatabaseOperations:
    """
    This class provides methods for performing CRUD operations on a database using SQLAlchemy's asynchronous session.

    The methods include:

    - `create_one`: Creates a single record in the database.
    - `create_many`: Creates multiple records in the database.
    - `read_one`: Reads a single record from the database.
    - `read_many`: Reads multiple records from the database.
    - `update_one`: Updates a single record in the database.
    - `update_many`: Updates multiple records in the database.
    - `delete_one`: Deletes a single record from the database.
    - `delete_many`: Deletes multiple records from the database.
    - `read_query`: Executes a fetch query on the database and returns a list of records that match the query.
    - `read_multi_query`: Executes multiple fetch queries on the database and returns a dictionary of results for each query.
    - `count_query`: Counts the number of records that match a given query.
    - `get_column_details`: Gets the details of the columns in a table.
    - `get_primary_keys`: Gets the primary keys of a table.
    - `get_table_names`: Gets the names of all tables in the database.

    Examples:
    ```python
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
    # create one record
    data = await db_ops.create_one(User(name='John Doe'))
    # read one record
    record = await db_ops.read_one(User, 1)
    ```
    """

    def __init__(self, async_db: AsyncDatabase):
        """
        Initializes a new instance of the DatabaseOperations class.

        Args:
            async_db (module_name.AsyncDatabase): An instance of the
            AsyncDatabase class for performing asynchronous database operations.

        Example:
        ```python
        from dsg_lib.async_database_functions import (
        async_database,
        base_schema,
        database_config,
        database_operations,
        )

        config = {
            # "database_uri": "postgresql+asyncpg://postgres:postgres@postgresdb/postgres",
            "database_uri": "sqlite+aiosqlite:///:memory:?cache=shared",
            "echo": False,
            "future": True,
            # "pool_pre_ping": True,
            # "pool_size": 10,
            # "max_overflow": 10,
            "pool_recycle": 3600,
            # "pool_timeout": 30,
        }

        db_config = database_config.DBConfig(config)

        async_db = async_database.AsyncDatabase(db_config)

        db_ops = database_operations.DatabaseOperations(async_db)

        ```
        """
        # Log the start of the initialization
        logger.debug("Initializing DatabaseOperations instance")

        # Store the AsyncDatabase instance in the async_db attribute This
        # instance will be used for performing asynchronous database operations
        self.async_db = async_db

        # Log the successful initialization
        logger.debug("DatabaseOperations instance initialized successfully")

    async def get_columns_details(self, table):
        """
        Retrieves the details of the columns of a given table.

        This asynchronous method accepts a table object and returns a
        dictionary. Each key in the dictionary is a column name from the table,
        and the corresponding value is another dictionary containing details
        about that column, such as type, if it's nullable, if it's a primary
        key, if it's unique, its autoincrement status, and its default value.

        Args:
            table (Table): An instance of the SQLAlchemy Table class
            representing the database table for which column details are
            required.

        Returns:
            dict: A dictionary where each key is a column name, and each value
            is a dictionary with the column's details.

        Raises:
            Exception: If any error occurs during the database operation.

        Example:
        ```python
        from sqlalchemy import Table, MetaData, Column,
        Integer, String from dsg_lib.async_database_functions import module_name metadata = MetaData()
        my_table = Table('my_table', metadata,
                        Column('id', Integer, primary_key=True), Column('name',
                        String))

        from dsg_lib.async_database_functions import (
            async_database,
            base_schema,
            database_config,
            database_operations,
        )
        # Create a DBConfig instance
        config = {
            # "database_uri": "postgresql+asyncpg://postgres:postgres@postgresdb/postgres",
            "database_uri": "sqlite+aiosqlite:///:memory:?cache=shared",
            "echo": False,
            "future": True,
            # "pool_pre_ping": True,
            # "pool_size": 10,
            # "max_overflow": 10,
            "pool_recycle": 3600,
            # "pool_timeout": 30,
        }
        # create database configuration
        db_config = database_config.DBConfig(config)
        # Create an AsyncDatabase instance
        async_db = async_database.AsyncDatabase(db_config)
        # Create a DatabaseOperations instance
        db_ops = database_operations.DatabaseOperations(async_db)
        # get columns details
        columns = await db_ops.get_columns_details(my_table)
        ```
        """
        # Log the start of the operation
        logger.debug(
            f"Starting get_columns_details operation for table: {table.__name__}"
        )

        try:
            # Log the start of the column retrieval
            logger.debug(f"Getting columns for table: {table.__name__}")

            # Retrieve the details of the columns and store them in a dictionary
            # The keys are the column names and the values are dictionaries
            # containing the column details
            columns = {
                c.name: {
                    "type": str(c.type),
                    "nullable": c.nullable,
                    "primary_key": c.primary_key,
                    "unique": c.unique,
                    "autoincrement": c.autoincrement,
                    "default": (
                        str(c.default.arg)
                        if c.default is not None and not callable(c.default.arg)
                        else None
                    ),
                }
                for c in table.__table__.columns
            }

            # Log the successful column retrieval
            logger.debug(f"Successfully retrieved columns for table: {table.__name__}")

            return columns
        except Exception as ex:  # pragma: no cover
            # Handle any exceptions that occur during the column retrieval
            logger.error(
                f"An error occurred while getting columns for table: {table.__name__}"
            )  # pragma: no cover
            return handle_exceptions(ex)  # pragma: no cover

    async def get_primary_keys(self, table):
        """
        Retrieves the primary keys of a given table.

        This asynchronous method accepts a table object and returns a list
        containing the names of its primary keys. It is useful for understanding
        the structure of the table and for operations that require knowledge of
        the primary keys.

        Args:
            table (Table): An instance of the SQLAlchemy Table class
            representing the database table for which primary keys are required.

        Returns:
            list: A list containing the names of the primary keys of the table.

        Raises:
            Exception: If any error occurs during the database operation.

        Example:
            ```python
            from sqlalchemy import Table, MetaData, Column, Integer,
                String from dsg_lib.async_database_functions import module_name metadata = MetaData()
                my_table = Table('my_table', metadata,
                                Column('id', Integer, primary_key=True),
                                Column('name', String, primary_key=True))
            from dsg_lib.async_database_functions import (
                async_database,
                base_schema,
                database_config,
                database_operations,
            )
            # Create a DBConfig instance
            config = {
                # "database_uri": "postgresql+asyncpg://postgres:postgres@postgresdb/postgres",
                "database_uri": "sqlite+aiosqlite:///:memory:?cache=shared",
                "echo": False,
                "future": True,
                # "pool_pre_ping": True,
                # "pool_size": 10,
                # "max_overflow": 10,
                "pool_recycle": 3600,
                # "pool_timeout": 30,
            }
            # create database configuration
            db_config = database_config.DBConfig(config)
            # Create an AsyncDatabase instance
            async_db = async_database.AsyncDatabase(db_config)
            # Create a DatabaseOperations instance
            db_ops = database_operations.DatabaseOperations(async_db)

            # get primary keys
            primary_keys = await db_ops.get_primary_keys(my_table)
            ```
        """
        # Log the start of the operation
        logger.debug(f"Starting get_primary_keys operation for table: {table.__name__}")

        try:
            # Log the start of the primary key retrieval
            logger.debug(f"Getting primary keys for table: {table.__name__}")

            # Retrieve the primary keys and store them in a list
            primary_keys = table.__table__.primary_key.columns.keys()

            # Log the successful primary key retrieval
            logger.debug(f"Primary keys retrieved successfully: {primary_keys}")

            return primary_keys

        except Exception as ex:  # pragma: no cover
            # Handle any exceptions that occur during the primary key retrieval
            logger.error(f"Exception occurred: {ex}")  # pragma: no cover
            return handle_exceptions(ex)  # pragma: no cover

    async def get_table_names(self):
        """
        Retrieves the names of all tables in the database.

        This asynchronous method returns a list containing the names of all
        tables in the database. It is useful for database introspection,
        allowing the user to know which tables are available in the current
        database context.

        Returns:
            list: A list containing the names of all tables in the database.

        Raises:
            Exception: If any error occurs during the database operation.

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
                # "database_uri": "postgresql+asyncpg://postgres:postgres@postgresdb/postgres",
                "database_uri": "sqlite+aiosqlite:///:memory:?cache=shared",
                "echo": False,
                "future": True,
                # "pool_pre_ping": True,
                # "pool_size": 10,
                # "max_overflow": 10,
                "pool_recycle": 3600,
                # "pool_timeout": 30,
            }
            # create database configuration
            db_config = database_config.DBConfig(config)
            # Create an AsyncDatabase instance
            async_db = async_database.AsyncDatabase(db_config)
            # Create a DatabaseOperations instance
            db_ops = database_operations.DatabaseOperations(async_db)
            # get table names
            table_names = await db_ops.get_table_names()
            ```
        """
        # Log the start of the operation
        logger.debug("Starting get_table_names operation")

        try:
            # Log the start of the table name retrieval
            logger.debug("Retrieving table names")

            # Retrieve the table names and store them in a list The keys of the
            # metadata.tables dictionary are the table names
            table_names = list(self.async_db.Base.metadata.tables.keys())

            # Log the successful table name retrieval
            logger.debug(f"Table names retrieved successfully: {table_names}")

            return table_names

        except Exception as ex:  # pragma: no cover
            # Handle any exceptions that occur during the table name retrieval
            logger.error(f"Exception occurred: {ex}")  # pragma: no cover
            return handle_exceptions(ex)  # pragma: no cover

    async def create_one(self, record):
        """
        Adds a single record to the database.

        This asynchronous method accepts a record object and adds it to the
        database. If the operation is successful, it returns the added record.
        The method is useful for inserting a new row into a database table.

        Parameters:
            record (Base): An instance of the SQLAlchemy declarative base class
            representing the record to be added to the database.

        Returns:
            Base: The instance of the record that was added to the database.

        Raises:
            Exception: If any error occurs during the database operation.

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
                # "database_uri": "postgresql+asyncpg://postgres:postgres@postgresdb/postgres",
                "database_uri": "sqlite+aiosqlite:///:memory:?cache=shared",
                "echo": False,
                "future": True,
                # "pool_pre_ping": True,
                # "pool_size": 10,
                # "max_overflow": 10,
                "pool_recycle": 3600,
                # "pool_timeout": 30,
            }
            # create database configuration
            db_config = database_config.DBConfig(config)
            # Create an AsyncDatabase instance
            async_db = async_database.AsyncDatabase(db_config)
            # Create a DatabaseOperations instance
            db_ops = database_operations.DatabaseOperations(async_db)
            # create one record
            record = await db_ops.create_one(User(name='John Doe'))
            ```
        """
        # Log the start of the operation
        logger.debug("Starting create_one operation")

        try:
            # Start a new database session
            async with self.async_db.get_db_session() as session:
                # Log the record being added
                logger.debug(f"Adding record to session: {record.__dict__}")

                # Add the record to the session and commit the changes
                session.add(record)
                await session.commit()

                # Log the successful record addition
                logger.debug(f"Record added successfully: {record}")

                return record

        except Exception as ex:
            # Handle any exceptions that occur during the record addition
            logger.error(f"Exception occurred: {ex}")
            return handle_exceptions(ex)

    async def create_many(self, records):
        """
        Adds multiple records to the database.

        This asynchronous method accepts a list of record objects and adds them
        to the database. If the operation is successful, it returns the added
        records. This method is useful for bulk inserting multiple rows into a
        database table efficiently.

        Parameters:
            records (list[Base]): A list of instances of the SQLAlchemy
            declarative base class, each representing a record to be added to
            the database.

        Returns:
            list[Base]: A list of instances of the records that were added to
            the database.

        Raises:
            Exception: If any error occurs during the database operation.

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
                # "database_uri": "postgresql+asyncpg://postgres:postgres@postgresdb/postgres",
                "database_uri": "sqlite+aiosqlite:///:memory:?cache=shared",
                "echo": False,
                "future": True,
                # "pool_pre_ping": True,
                # "pool_size": 10,
                # "max_overflow": 10,
                "pool_recycle": 3600,
                # "pool_timeout": 30,
            }
            # create database configuration
            db_config = database_config.DBConfig(config)
            # Create an AsyncDatabase instance
            async_db = async_database.AsyncDatabase(db_config)
            # Create a DatabaseOperations instance
            db_ops = database_operations.DatabaseOperations(async_db)
            # create many records
            records = await db_ops.create_many([User(name='John Doe'), User(name='Jane Doe')])
            ```
        """
        # Log the start of the operation
        logger.debug("Starting create_many operation")

        try:
            # Start a timer to measure the operation time
            t0 = time.time()

            # Start a new database session
            async with self.async_db.get_db_session() as session:
                # Log the number of records being added
                logger.debug(f"Adding {len(records)} records to session")

                # Add the records to the session and commit the changes
                session.add_all(records)
                await session.commit()

                # Log the added records
                records_data = [record.__dict__ for record in records]
                logger.debug(f"Records added to session: {records_data}")

                # Calculate the operation time and log the successful record
                # addition
                num_records = len(records)
                t1 = time.time() - t0
                logger.debug(
                    f"Record operations were successful. {num_records} records were created in {t1:.4f} seconds."
                )

                return records

        except Exception as ex:
            # Handle any exceptions that occur during the record addition
            logger.error(f"Exception occurred: {ex}")
            return handle_exceptions(ex)

    async def count_query(self, query):
        """
        Executes a count query on the database and returns the number of records
        that match the query.

        This asynchronous method accepts a SQLAlchemy `Select` query object and
        returns the count of records that match the query. This is particularly
        useful for getting the total number of records that satisfy certain
        conditions without actually fetching the records themselves.

        Parameters:
            query (Select): A SQLAlchemy `Select` query object specifying the
            conditions to count records for.

        Returns:
            int: The number of records that match the query.

        Raises:
            Exception: If any error occurs during the execution of the query.

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
                # "database_uri": "postgresql+asyncpg://postgres:postgres@postgresdb/postgres",
                "database_uri": "sqlite+aiosqlite:///:memory:?cache=shared",
                "echo": False,
                "future": True,
                # "pool_pre_ping": True,
                # "pool_size": 10,
                # "max_overflow": 10,
                "pool_recycle": 3600,
                # "pool_timeout": 30,
            }
            # create database configuration
            db_config = database_config.DBConfig(config)
            # Create an AsyncDatabase instance
            async_db = async_database.AsyncDatabase(db_config)
            # Create a DatabaseOperations instance
            db_ops = database_operations.DatabaseOperations(async_db)
            # count query
            count = await db_ops.count_query(select(User).where(User.age > 30))
            ```
        """
        # Log the start of the operation
        logger.debug("Starting count_query operation")

        try:
            # Start a new database session
            async with self.async_db.get_db_session() as session:
                # Log the query being executed
                logger.debug(f"Executing count query: {query}")

                # Execute the count query and retrieve the count
                result = await session.execute(
                    select(func.count()).select_from(query.subquery())
                )
                count = result.scalar()

                # Log the successful query execution
                logger.debug(f"Count query executed successfully. Result: {count}")

                return count

        except Exception as ex:
            # Handle any exceptions that occur during the query execution
            logger.error(f"Exception occurred: {ex}")
            return handle_exceptions(ex)

    async def read_one_record(self, query):
        """
        Retrieves a single record from the database based on the provided query.

        This asynchronous method accepts a SQL query object and returns the
        first record that matches the query. If no record matches the query, it
        returns None. This method is useful for fetching specific data
        when the expected result is a single record.

        Parameters:
            query (Select): An instance of the SQLAlchemy Select class,
            representing the query to be executed.

        Returns:
            Result: The first record that matches the query or None if no record matches.

        Raises:
            Exception: If any error occurs during the database operation.

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
                # "database_uri": "postgresql+asyncpg://postgres:postgres@postgresdb/postgres",
                "database_uri": "sqlite+aiosqlite:///:memory:?cache=shared",
                "echo": False,
                "future": True,
                # "pool_pre_ping": True,
                # "pool_size": 10,
                # "max_overflow": 10,
                "pool_recycle": 3600,
                # "pool_timeout": 30,
            }
            # create database configuration
            db_config = database_config.DBConfig(config)
            # Create an AsyncDatabase instance
            async_db = async_database.AsyncDatabase(db_config)
            # Create a DatabaseOperations instance
            db_ops = database_operations.DatabaseOperations(async_db)
            # read one record
            record = await db_ops.read_one_record(select(User).where(User.name == 'John Doe'))
            ```
        """
        # Log the start of the operation
        logger.debug(f"Starting read_one_record operation for {query}")

        try:
            # Start a new database session
            async with self.async_db.get_db_session() as session:
                # Log the start of the record retrieval
                logger.debug(f"Getting record with query: {query}")

                # Execute the query and retrieve the first record
                result = await session.execute(query)
                record = result.scalar_one()

                # Log the successful record retrieval
                logger.debug(f"Record retrieved successfully: {record}")

                return record

        except NoResultFound:
            # No record was found
            logger.debug("No record found")
            return None

        except Exception as ex:  # pragma: no cover
            # Handle any exceptions that occur during the record retrieval
            logger.error(f"Exception occurred: {ex}")  # pragma: no cover
            return handle_exceptions(ex)  # pragma: no cover

    async def read_query(self, query):
        """
        Executes a fetch query on the database and returns a list of records
        that match the query.

        This asynchronous method accepts a SQLAlchemy `Select` query object.
        It returns a list of records that match the query.

        Parameters:
            query (Select): A SQLAlchemy `Select` query object specifying the
            conditions to fetch records for.

        Returns:
            list: A list of records that match the query.

        Raises:
            Exception: If any error occurs during the execution of the query.

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
            # read query
            records = await db_ops.read_query(select(User).where(User.age > 30))
            ```
        """
        # Log the start of the operation
        logger.debug("Starting read_query operation")

        try:
            # Start a new database session
            async with self.async_db.get_db_session() as session:
                # Log the query being executed
                logger.debug(f"Executing fetch query: {query}")

                # Execute the fetch query and retrieve the records
                result = await session.execute(query)
                records = result.scalars().all()
                logger.debug(f"read_query result: {records}")
                # Log the successful query execution
                if all(
                    isinstance(record, tuple) for record in records
                ):  # pragma: no cover
                    logger.debug(f"read_query result is a tuple {type(records)}")
                    # If all records are tuples, convert them to dictionaries
                    records_data = [
                        dict(zip(("request_group_id", "count"), record, strict=False))
                        for record in records
                    ]
                else:
                    logger.debug(f"read_query result is a dictionary {type(records)}")
                    # Otherwise, try to convert the records to dictionaries using the __dict__ attribute
                    records_data = [record.__dict__ for record in records]

                logger.debug(
                    f"Fetch query executed successfully. Records: {records_data}"
                )

                return records

        except Exception as ex:
            # Handle any exceptions that occur during the query execution
            logger.error(f"Exception occurred: {ex}")
            return handle_exceptions(ex)

    async def read_multi_query(self, queries: Dict[str, str]):
        """
        Executes multiple fetch queries on the database and returns a dictionary
        of results for each query.

        This asynchronous method takes a dictionary where each key is a query
        name and each value is a SQLAlchemy `Select` query object. The method executes each
        query and returns a dictionary where each key is the query name, and the
        corresponding value is a list of records that match that query.

        Parameters:
            queries (Dict[str, Select]): A dictionary of SQLAlchemy `Select`
            query objects.

        Returns:
            dict: A dictionary where each key is a query name and each value is
            a list of records that match the query.

        Raises:
            Exception: If any error occurs during the execution of the queries.

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
            # read multi query
            queries = {
                "query1": select(User).where(User.age > 30),
                "query2": select(User).where(User.age < 20),
            }
            results = await db_ops.read_multi_query(queries)
            ```
        """
        # Log the start of the operation
        logger.debug("Starting read_multi_query operation")

        try:
            results = {}
            # Start a new database session
            async with self.async_db.get_db_session() as session:
                for query_name, query in queries.items():
                    # Log the query being executed
                    logger.debug(f"Executing fetch query: {query}")

                    # Execute the fetch query and retrieve the records
                    result = await session.execute(query)
                    data = result.scalars().all()

                    # Convert the records to dictionaries for logging
                    data_dicts = [record.__dict__ for record in data]
                    logger.debug(f"Fetch result for query '{query_name}': {data_dicts}")

                    # Store the records in the results dictionary
                    results[query_name] = data
            return results

        except Exception as ex:
            # Handle any exceptions that occur during the query execution
            logger.error(f"Exception occurred: {ex}")
            return handle_exceptions(ex)

    async def update_one(self, table, record_id: str, new_values: dict):
        """
        Updates a single record in the database identified by its ID.

        This asynchronous method takes a SQLAlchemy `Table` object, a record ID,
        and a dictionary of new values to update the record. It updates the
        specified record in the given table with the new values. The method does
        not allow updating certain fields, such as 'id' or 'date_created'.

        Parameters:
            table (Table): The SQLAlchemy `Table` object representing the table
            in the database. record_id (str): The ID of the record to be
            updated. new_values (dict): A dictionary containing the fields to
            update and their new values.

        Returns:
            Base: The updated record if successful; otherwise, an error
            dictionary.

        Raises:
            Exception: If any error occurs during the update operation.

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
                # "database_uri": "postgresql+asyncpg://postgres:postgres@postgresdb/postgres",
                "database_uri": "sqlite+aiosqlite:///:memory:?cache=shared",
                "echo": False,
                "future": True,
                # "pool_pre_ping": True,
                # "pool_size": 10,
                # "max_overflow": 10,
                "pool_recycle": 3600,
                # "pool_timeout": 30,
            }
            # create database configuration
            db_config = database_config.DBConfig(config)
            # Create an AsyncDatabase instance
            async_db = async_database.AsyncDatabase(db_config)
            # Create a DatabaseOperations instance
            db_ops = database_operations.DatabaseOperations(async_db)
            # update one record
            record = await db_ops.update_one(User, 1, {'name': 'John Smith'})
            ```
        """
        non_updatable_fields = ["id", "date_created"]

        # Log the start of the operation
        logger.debug(
            f"Starting update_one operation for record_id: {record_id} in table: {table.__name__}"
        )

        try:
            # Start a new database session
            async with self.async_db.get_db_session() as session:
                # Log the record being fetched
                logger.debug(f"Fetching record with id: {record_id}")

                # Fetch the record
                record = await session.get(table, record_id)
                if not record:
                    # Log the error if no record is found
                    logger.error(f"No record found with pkid: {record_id}")
                    return {
                        "error": "Record not found",
                        "details": f"No record found with pkid {record_id}",
                    }

                # Log the record being updated
                logger.debug(f"Updating record with new values: {new_values}")

                # Update the record with the new values
                for key, value in new_values.items():
                    if key not in non_updatable_fields:
                        setattr(record, key, value)
                await session.commit()

                # Log the successful record update
                logger.debug(f"Record updated successfully: {record.pkid}")
                return record

        except Exception as ex:
            # Handle any exceptions that occur during the record update
            logger.error(f"Exception occurred: {ex}")
            return handle_exceptions(ex)

    async def delete_one(self, table, record_id: str):
        """
        Deletes a single record from the database based on the provided table
        and record ID.

        This asynchronous method accepts a SQLAlchemy `Table` object and a
        record ID. It attempts to delete the record with the given ID from the
        specified table. If the record is successfully deleted, it returns a
        success message. If no record with the given ID is found, it returns an
        error message.

        Args:
            table (Table): An instance of the SQLAlchemy `Table` class
            representing the database table from which the record will be
            deleted. record_id (str): The ID of the record to be deleted.

        Returns:
            dict: A dictionary containing a success message if the record was
            deleted successfully, or an error message if the record was not
            found or an exception occurred.

        Raises:
            Exception: If any error occurs during the delete operation.

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
                # "database_uri": "postgresql+asyncpg://postgres:postgres@postgresdb/postgres",
                "database_uri": "sqlite+aiosqlite:///:memory:?cache=shared",
                "echo": False,
                "future": True,
                # "pool_pre_ping": True,
                # "pool_size": 10,
                # "max_overflow": 10,
                "pool_recycle": 3600,
                # "pool_timeout": 30,
            }
            # create database configuration
            db_config = database_config.DBConfig(config)
            # Create an AsyncDatabase instance
            async_db = async_database.AsyncDatabase(db_config)
            # Create a DatabaseOperations instance
            db_ops = database_operations.DatabaseOperations(async_db)
            # delete one record
            result = await db_ops.delete_one(User, 1)
            ```
        """
        # Log the start of the operation
        logger.debug(
            f"Starting delete_one operation for record_id: {record_id} in table: {table.__name__}"
        )

        try:
            # Start a new database session
            async with self.async_db.get_db_session() as session:
                # Log the record being fetched
                logger.debug(f"Fetching record with id: {record_id}")

                # Fetch the record
                record = await session.get(table, record_id)

                # If the record doesn't exist, return an error
                if not record:
                    logger.error(f"No record found with pkid: {record_id}")
                    return {
                        "error": "Record not found",
                        "details": f"No record found with pkid {record_id}",
                    }

                # Log the record being deleted
                logger.debug(f"Deleting record with id: {record_id}")

                # Delete the record
                await session.delete(record)

                # Log the successful record deletion from the session
                logger.debug(f"Record deleted from session: {record}")

                # Log the start of the commit
                logger.debug(
                    f"Committing changes to delete record with id: {record_id}"
                )

                # Commit the changes
                await session.commit()

                # Log the successful record deletion
                logger.debug(f"Record deleted successfully: {record_id}")

                return {"success": "Record deleted successfully"}

        except Exception as ex:
            # Handle any exceptions that occur during the record deletion
            logger.error(f"Exception occurred: {ex}")
            return handle_exceptions(ex)

    async def delete_many(
        self,
        table: Type[DeclarativeMeta],
        id_column_name: str = "pkid",
        id_values: List[int] = None,
    ) -> int:
        """
        Deletes multiple records from the specified table in the database.

        This method takes a table, an optional id column name, and a list of id values. It deletes the records in the table where the id column matches any of the id values in the list.

        Args:
            table (Type[DeclarativeMeta]): The table from which to delete records.
            id_column_name (str, optional): The name of the id column in the table. Defaults to "pkid".
            id_values (List[int], optional): A list of id values for the records to delete. Defaults to [].

        Returns:
            int: The number of records deleted from the table.

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
        # Delete multiple records
        deleted_count = await db_ops.delete_many(User, 'id', [1, 2, 3])
        print(f"Deleted {deleted_count} records.")
        ```
        """
        if id_values is None:  # pragma: no cover
            id_values = []
        try:
            # Start a timer to measure the operation time
            t0 = time.time()

            # Start a new database session
            async with self.async_db.get_db_session() as session:
                # Log the number of records being deleted
                logger.debug(f"Deleting {len(id_values)} records from session")

                # Create delete statement
                stmt = delete(table).where(
                    getattr(table, id_column_name).in_(id_values)
                )

                # Execute the delete statement and fetch result
                result = await session.execute(stmt)

                # Commit the changes
                await session.commit()

                # Get the count of deleted records
                deleted_count = result.rowcount

                # Log the deleted records
                logger.debug(f"Records deleted from session: {deleted_count}")

                # Calculate the operation time and log the successful record deletion
                t1 = time.time() - t0
                logger.debug(
                    f"Record operations were successful. {deleted_count} records were deleted in {t1:.4f} seconds."
                )

                return deleted_count

        except Exception as ex:
            # Handle any exceptions that occur during the record deletion
            logger.error(f"Exception occurred: {ex}")
            return handle_exceptions(ex)
