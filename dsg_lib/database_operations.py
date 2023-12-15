# -*- coding: utf-8 -*-
"""
This Python module, `database_operations.py`, provides a class `DatabaseOperations` for managing asynchronous database operations using SQLAlchemy and AsyncDatabase.

The `DatabaseOperations` class provides methods for executing various types of database operations, including:
- Count queries
- Fetch queries
- Record insertions
- Updates
- Deletions

It uses an instance of the `AsyncDatabase` class to perform these operations asynchronously.

The module imports necessary modules and packages from `sqlalchemy` for database operations and error handling. It also imports `AsyncDatabase` from the local module `async_database`.

The `DatabaseOperations` class has the following methods:
- `__init__`: Initializes a new instance of the `DatabaseOperations` class.
- `get_columns_details`: Retrieves the details of the columns of a given table.
- `get_primary_keys`: Retrieves the primary keys of a given table.
- `get_table_names`: Retrieves the names of all tables in the database.
- `get_one_record`: Retrieves a single record from the database based on a given query.
- `create_one`: Adds a single record to the database.
- `create_many`: Adds multiple records to the database.
- `count_query`: Executes a count query and returns the result.
- `read_query`: Executes a fetch query and returns the result.
- `read_multi_query`: Executes multiple fetch queries and returns the results.
- `update_one`: Updates a single record in the database.
- `delete_one`: Deletes a single record from the database.

Each method is designed to handle exceptions and log errors and information messages using the logging module.

This module is designed to be used in an asynchronous context and requires Python 3.7+.
"""

import time  # Importing time module to work with times

# Importing Dict and List from typing for type hinting
from typing import Dict

from packaging import version as packaging_version

from loguru import logger

# Importing AsyncDatabase class from local module async_database
from .async_database import AsyncDatabase


def import_sqlalchemy():
    """
    Tries to import SQLAlchemy and its components.

    This function attempts to import SQLAlchemy and its components. If SQLAlchemy is not installed or if the installed version is not compatible, it sets the imported components to None.

    Returns:
    tuple: A tuple containing the imported components from SQLAlchemy. If import fails, all are set to None.
    """
    # Define the minimum required version of SQLAlchemy
    min_version = "1.4.0"

    try:
        # Try to import necessary components from SQLAlchemy
        import sqlalchemy
        from sqlalchemy import func
        from sqlalchemy.exc import IntegrityError, SQLAlchemyError
        from sqlalchemy.future import select
    except ImportError:
        # If import fails, set all components to None
        func = select = sqlalchemy = None

    # Check if SQLAlchemy is imported and if its version is compatible
    if sqlalchemy is not None and packaging_version.parse(
        sqlalchemy.__version__
    ) < packaging_version.parse(min_version):
        # If the version is not compatible, raise an ImportError
        raise ImportError(
            f"SQLAlchemy version >= {min_version} required, run `pip install --upgrade sqlalchemy`"
        )

    # Return the imported components
    return sqlalchemy, func, IntegrityError, SQLAlchemyError, select


# Call the function at the module level to import the components
sqlalchemy, func, IntegrityError, SQLAlchemyError, select = import_sqlalchemy()


def handle_exceptions(ex: Exception) -> Dict[str, str]:
    """
    Handles exceptions for database operations.

    This function checks the type of the exception and logs an appropriate error message. It also returns a dictionary containing the error details.

    Parameters:
    ex (Exception): The exception to handle.

    Returns:
    dict: A dictionary containing the error details. The dictionary has two keys: 'error' and 'details'.
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
    A class used to manage the database operations.

    This class provides methods for executing various types of database operations, including count queries, fetch queries, record insertions, updates, and deletions.

    Attributes
    ----------
    async_db : AsyncDatabase
        an instance of AsyncDatabase class for performing asynchronous database operations

    Methods
    -------
    __init__(self, async_db: AsyncDatabase):
        Initializes a new instance of the DatabaseOperations class.
    """

    def __init__(self, async_db: AsyncDatabase):
        """
        Initializes a new instance of the DatabaseOperations class.

        This method takes an instance of the AsyncDatabase class as input and stores it in the async_db attribute for later use in other methods.

        Parameters:
        async_db (AsyncDatabase): An instance of the AsyncDatabase class for performing asynchronous database operations.

        Returns: None
        """
        # Log the start of the initialization
        logger.debug("Initializing DatabaseOperations instance")

        # Store the AsyncDatabase instance in the async_db attribute
        # This instance will be used for performing asynchronous database operations
        self.async_db = async_db

        # Log the successful initialization
        logger.info("DatabaseOperations instance initialized successfully")

    async def get_columns_details(self, table):
        """
        Retrieves the details of the columns of a given table.

        This method takes a table as input and returns a dictionary containing the details of its columns.

        Parameters:
        table (Table): The table to get the column details from.

        Returns:
        dict: A dictionary containing the details of the columns. The keys are the column names and the values are dictionaries containing the column details.
        """
        # Log the start of the operation
        logger.debug(
            f"Starting get_columns_details operation for table: {table.__name__}"
        )

        try:
            # Log the start of the column retrieval
            logger.debug(f"Getting columns for table: {table.__name__}")

            # Retrieve the details of the columns and store them in a dictionary
            # The keys are the column names and the values are dictionaries containing the column details
            columns = {
                c.name: {
                    "type": str(c.type),
                    "nullable": c.nullable,
                    "primary_key": c.primary_key,
                    "unique": c.unique,
                    "autoincrement": c.autoincrement,
                    "default": str(c.default.arg)
                    if c.default is not None and not callable(c.default.arg)
                    else None,
                }
                for c in table.__table__.columns
            }

            # Log the successful column retrieval
            logger.info(f"Successfully retrieved columns for table: {table.__name__}")

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

        This method takes a table as input and returns a list containing the names of its primary keys.

        Parameters:
        table (Table): The table to get the primary keys from.

        Returns:
        list: A list containing the names of the primary keys.
        """
        # Log the start of the operation
        logger.debug(f"Starting get_primary_keys operation for table: {table.__name__}")

        try:
            # Log the start of the primary key retrieval
            logger.debug(f"Getting primary keys for table: {table.__name__}")

            # Retrieve the primary keys and store them in a list
            primary_keys = table.__table__.primary_key.columns.keys()

            # Log the successful primary key retrieval
            logger.info(f"Primary keys retrieved successfully: {primary_keys}")

            return primary_keys

        except Exception as ex:  # pragma: no cover
            # Handle any exceptions that occur during the primary key retrieval
            logger.error(f"Exception occurred: {ex}")  # pragma: no cover
            return handle_exceptions(ex)  # pragma: no cover

    async def get_table_names(self):
        """
        Retrieves the names of all tables in the database.

        This method returns a list containing the names of all tables in the database.

        Returns:
        list: A list containing the names of all tables.
        """
        # Log the start of the operation
        logger.debug("Starting get_table_names operation")

        try:
            # Log the start of the table name retrieval
            logger.debug("Retrieving table names")

            # Retrieve the table names and store them in a list
            # The keys of the metadata.tables dictionary are the table names
            table_names = list(self.async_db.Base.metadata.tables.keys())

            # Log the successful table name retrieval
            logger.info(f"Table names retrieved successfully: {table_names}")

            return table_names

        except Exception as ex:  # pragma: no cover
            # Handle any exceptions that occur during the table name retrieval
            logger.error(f"Exception occurred: {ex}")  # pragma: no cover
            return handle_exceptions(ex)  # pragma: no cover

    async def get_one_record(self, query):
        """
        Retrieves a single record from the database based on the provided query.

        This method takes a query as input and returns the first record that matches the query. If no record matches the query, it raises an exception.

        Parameters:
        query (Select): The query to execute.

        Returns:
        Result: The first record that matches the query.
        """
        # Log the start of the operation
        logger.debug(f"Starting get_one_record operation for {query}")

        try:
            # Start a new database session
            async with self.async_db.get_db_session() as session:
                # Log the start of the record retrieval
                logger.debug(f"Getting record with query: {query}")

                # Execute the query and retrieve the first record
                result = await session.execute(query)
                record = result.scalar_one()

                # Log the successful record retrieval
                logger.info(f"Record retrieved successfully: {record}")

                return record

        except Exception as ex:  # pragma: no cover
            # Handle any exceptions that occur during the record retrieval
            logger.error(f"Exception occurred: {ex}")  # pragma: no cover
            return handle_exceptions(ex)  # pragma: no cover

    async def create_one(self, record):
        """
        Adds a single record to the database.

        This method takes a record as input and adds it to the database. If the operation is successful, it returns the added record.

        Parameters:
        record (Base): The record to add.

        Returns:
        Base: The added record.
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
                logger.info(f"Record added successfully: {record}")

                return record

        except Exception as ex:
            # Handle any exceptions that occur during the record addition
            logger.error(f"Exception occurred: {ex}")
            return handle_exceptions(ex)

    async def create_many(self, records):
        """
        Adds multiple records to the database.

        This method takes a list of records as input and adds them to the database. If the operation is successful, it returns the added records.

        Parameters:
        records (list): The records to add.

        Returns:
        list: The added records.
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

                # Calculate the operation time and log the successful record addition
                num_records = len(records)
                t1 = time.time() - t0
                logger.info(
                    f"Record operations were successful. {num_records} records were created in {t1:.4f} seconds."
                )

                return records

        except Exception as ex:
            # Handle any exceptions that occur during the record addition
            logger.error(f"Exception occurred: {ex}")
            return handle_exceptions(ex)

    async def count_query(self, query):
        """
        Executes a count query on the database.

        This method takes a query as input and returns the count of records that match the query.

        Parameters:
        query (Select): The query to execute.

        Returns:
        int: The count of records that match the query.
        """
        # Log the start of the operation
        logger.debug("Starting count_query operation")

        try:
            # Start a new database session
            async with self.async_db.get_db_session() as session:
                # Log the query being executed
                logger.debug(f"Executing count query: {query}")

                # Execute the count query and retrieve the count
                result = await session.execute(select(func.count()).select_from(query))
                count = result.scalar()

                # Log the successful query execution
                logger.info(f"Count query executed successfully. Result: {count}")

                return count

        except Exception as ex:
            # Handle any exceptions that occur during the query execution
            logger.error(f"Exception occurred: {ex}")
            return handle_exceptions(ex)

    async def read_query(self, query, limit=500, offset=0):
        """
        Executes a fetch query on the database.

        This method takes a query, a limit, and an offset as input and returns the records that match the query. The number of records returned is limited by the limit, and the offset determines the starting point of the records returned.

        Parameters:
        query (Select): The query to execute.
        limit (int): The maximum number of records to return.
        offset (int): The number of records to skip before starting to return records.

        Returns:
        list: The records that match the query.
        """
        # Log the start of the operation
        logger.debug("Starting read_query operation")

        try:
            # Start a new database session
            async with self.async_db.get_db_session() as session:
                # Log the query being executed
                logger.debug(
                    f"Executing fetch query: {query} with limit: {limit} and offset: {offset}"
                )

                # Execute the fetch query and retrieve the records
                result = await session.execute(query.limit(limit).offset(offset))
                records = result.scalars().all()

                # Log the successful query execution
                records_data = [record.__dict__ for record in records]
                logger.info(
                    f"Fetch query executed successfully. Records: {records_data}"
                )

                return records

        except Exception as ex:
            # Handle any exceptions that occur during the query execution
            logger.error(f"Exception occurred: {ex}")
            return handle_exceptions(ex)

    async def read_multi_query(self, queries: Dict[str, str], limit=500, offset=0):
        """
        Executes multiple fetch queries on the database.

        This method takes a dictionary of queries, a limit, and an offset as input and returns the records that match each query. The number of records returned for each query is limited by the limit, and the offset determines the starting point of the records returned.

        Parameters:
        queries (Dict[str, str]): The queries to execute.
        limit (int): The maximum number of records to return for each query.
        offset (int): The number of records to skip before starting to return records for each query.

        Returns:
        dict: The records that match each query.
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
                    result = await session.execute(query.limit(limit).offset(offset))
                    data = result.scalars().all()

                    # Convert the records to dictionaries for logging
                    data_dicts = [record.__dict__ for record in data]
                    logger.debug(f"Fetch result for query '{query_name}': {data_dicts}")

                    # Log the successful query execution
                    logger.info(
                        f"Fetch query executed successfully: {query_name} with {len(data)} records"
                    )

                    # Store the records in the results dictionary
                    results[query_name] = data
            return results

        except Exception as ex:
            # Handle any exceptions that occur during the query execution
            logger.error(f"Exception occurred: {ex}")
            return handle_exceptions(ex)

    async def update_one(self, table, record_id: str, new_values: dict):
        """
        Updates a single record in the database.

        This method takes a table, a record ID, and a dictionary of new values as input and updates the record in the table with the new values. The record ID and date created fields are not updatable.

        Parameters:
        table (Table): The table that contains the record.
        record_id (str): The ID of the record to update.
        new_values (dict): The new values to update the record with.

        Returns:
        Base: The updated record.
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
                logger.info(f"Record updated successfully: {record.pkid}")
                return record

        except Exception as ex:
            # Handle any exceptions that occur during the record update
            logger.error(f"Exception occurred: {ex}")
            return handle_exceptions(ex)

    async def delete_one(self, table, record_id: str):
        """
        Deletes a single record from the database.

        This method takes a table and a record ID as input and deletes the record from the table. If no record with the given ID exists in the table, it returns an error.

        Parameters:
        table (Table): The table that contains the record.
        record_id (str): The ID of the record to delete.

        Returns:
        dict: A dictionary containing a success message if the record was deleted successfully, or an error message if the record was not found or an exception occurred.
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
                logger.info(f"Record deleted successfully: {record_id}")

                return {"success": "Record deleted successfully"}

        except Exception as ex:
            # Handle any exceptions that occur during the record deletion
            logger.error(f"Exception occurred: {ex}")
            return handle_exceptions(ex)
