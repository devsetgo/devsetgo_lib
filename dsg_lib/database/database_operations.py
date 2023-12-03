# -*- coding: utf-8 -*-

"""
This Python module, database_operations.py, provides a class DatabaseOperations for managing asynchronous database operations using SQLAlchemy.

The DatabaseOperations class provides methods for executing various types of database operations, including count queries, fetch queries, record insertions, updates, and deletions. It uses an instance of the AsyncDatabase class to perform these operations asynchronously.

The module imports necessary modules and packages from sqlalchemy for database operations and error handling. It also imports AsyncDatabase from the local module async_database.

The DatabaseOperations class has the following methods:

__init__: Initializes a new instance of the DatabaseOperations class.
count_query: Executes a count query and returns the result.
read_query: Executes a fetch query and returns the result.
read_multi_query: Executes multiple fetch queries and returns the results.
create_one: Adds a single record to the database.
create_many: Adds multiple records to the database.
update_one: Updates a single record in the database.
delete_one: Deletes a single record from the database.
Each method is designed to handle exceptions and log errors and information messages using the logging module.

This module is designed to be used in an asynchronous context and requires Python 3.7+.
"""

import time  # Importing time module to work with times

# Importing Dict and List from typing for type hinting
from typing import Dict

# Importing MetaData and func from sqlalchemy for database operations
from sqlalchemy import func

# Importing specific exceptions from sqlalchemy for error handling
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

# Importing select from sqlalchemy for making select queries
from sqlalchemy.future import select

# import logging as logger  # Importing logging module for logging
from ..logger import logger

# Importing AsyncDatabase class from local module async_database
from .async_database import AsyncDatabase


def handle_exceptions(ex):
    """
    Handles exceptions for database operations.

    Parameters:
    ex (Exception): The exception to handle.

    Returns:
    dict: A dictionary containing the error details.
    """
    if isinstance(ex, IntegrityError):
        logger.error(f"IntegrityError occurred: {ex}")
        error_only = str(ex).split("[SQL:")[0]
        return {"error": "IntegrityError", "details": error_only}
    elif isinstance(ex, SQLAlchemyError):
        logger.error(f"SQLAlchemyError occurred: {ex}")
        error_only = str(ex).split("[SQL:")[0]
        return {"error": "SQLAlchemyError", "details": error_only}
    else:
        logger.error(f"Exception occurred: {ex}")
        return {"error": "General Exception", "details": str(ex)}


class DatabaseOperations:
    """
        The DatabaseOperations class provides methods for executing various types of database operations asynchronously using SQLAlchemy.

    This class is initialized with an instance of the AsyncDatabase class, which is used for performing the actual database operations.

    The class provides the following methods:

    __init__: Initializes a new instance of the DatabaseOperations class.
    count_query: Executes a count query and returns the result.
    read_query: Executes a fetch query and returns the result.
    read_multi_query: Executes multiple fetch queries and returns the results.
    create_one: Adds a single record to the database.
    create_many: Adds multiple records to the database.
    update_one: Updates a single record in the database.
    delete_one: Deletes a single record from the database.
    Each method is designed to handle exceptions and log errors and information messages using the logging module.

    This class is designed to be used in an asynchronous context and requires Python 3.7+.
    """

    def __init__(self, async_db: AsyncDatabase):
        """
        Initializes a new instance of the DatabaseOperations class.

        This method takes an instance of the AsyncDatabase class as input and stores it in the async_db attribute for later use in other methods.

        Parameters:
        async_db (AsyncDatabase): An instance of the AsyncDatabase class for performing asynchronous database operations.
        """
        # Store the AsyncDatabase instance in the async_db attribute
        logger.debug("Initializing DatabaseOperations instance")
        self.async_db = async_db
        logger.info("DatabaseOperations instance initialized successfully")

    async def create_one(self, record):
        """
        Adds a single record to the database.

        This method takes a dictionary representing a record, adds it to the database session, and commits the session. If the operation is successful, it returns the inserted record. If an error occurs during the operation, it raises a DatabaseOperationException.

        Parameters:
        record (dict): The record to add to the database, represented as a dictionary where the keys are the column names and the values are the corresponding column values.

        Returns:
        dict: The record that was added to the database.

        Raises:
        DatabaseOperationException: If an error occurs during the database operation.
        """
        logger.debug("Starting create_one operation")
        try:
            async with self.async_db.get_db_session() as session:
                # Add the record to the session and commit
                logger.debug(f"Adding record to session: {record.__dict__}")
                session.add(record)
                await session.commit()
                logger.info(f"Record added successfully: {record.id}")
                return record
        # Catch any exception that occurs during the operation
        except Exception as ex:
            # Call the handle_exceptions function to handle the exception.
            # This function checks the type of the exception and returns an appropriate error dictionary.
            # This way, we can handle multiple types of exceptions in a consistent manner across different methods.
            return handle_exceptions(ex)

    async def create_many(self, records):
        """
        Adds multiple records to the database.

        This method takes a list of dictionaries representing records, adds them all to the database session, and commits the session. If the operation is successful, it returns the inserted records. If an error occurs during the operation, it logs the error and returns a dictionary containing the error details.

        Parameters:
        records (list[dict]): The records to add to the database, each represented as a dictionary where the keys are the column names and the values are the corresponding column values.

        Returns:
        list[dict] or dict: The records that were added to the database if the operation is successful, otherwise a dictionary containing the error details.
        """
        logger.debug("Starting create_many operation")
        try:
            t0 = time.time()  # Record the start time of the operation
            async with self.async_db.get_db_session() as session:
                # Add all the records to the session and commit
                logger.debug(f"Adding {len(records)} records to session")
                session.add_all(records)  # Add all records to the session
                await session.commit()  # Commit the session to save the records to the database
                # Convert each record to a dictionary and log it
                records_data = [record.__dict__ for record in records]
                logger.debug(f"Records added to session: {records_data}")

                num_records = len(records)  # Get the number of records added
                t1 = time.time() - t0  # Calculate the time taken for the operation
                logger.info(
                    f"Record operations were successful. {num_records} records were created in {t1:.4f} seconds."
                )
                return records  # Return the list of records added
        # Catch any exception that occurs during the operation
        except Exception as ex:
            # Call the handle_exceptions function to handle the exception.
            # This function checks the type of the exception and returns an appropriate error dictionary.
            # This way, we can handle multiple types of exceptions in a consistent manner across different methods.
            return handle_exceptions(ex)

    async def count_query(self, query):
        """
        Executes a count query and returns the result.

        This method takes a SQLAlchemy query as input, executes it against the database to count the number of matching records, and returns the count. If an error occurs during the operation, it logs the error and returns a dictionary containing the error details.

        Parameters:
        query (sqlalchemy.sql.selectable.Select): The SQLAlchemy query to execute.

        Returns:
        int or dict: The count of matching records if the operation is successful, otherwise a dictionary containing the error details.
        """
        logger.debug("Starting count_query operation")
        try:
            async with self.async_db.get_db_session() as session:
                # Execute the count query
                logger.debug(f"Executing count query: {query}")
                result = await session.execute(select(func.count()).select_from(query))
                count = result.scalar()
                logger.info(f"Count query executed successfully. Result: {count}")
                return count
        # Catch any exception that occurs during the operation
        except Exception as ex:
            # Call the handle_exceptions function to handle the exception.
            # This function checks the type of the exception and returns an appropriate error dictionary.
            # This way, we can handle multiple types of exceptions in a consistent manner across different methods.
            return handle_exceptions(ex)

    async def read_query(self, query, limit=500, offset=0):
        """
        Executes a fetch query and returns the result.

        This method takes a SQLAlchemy query, a limit, and an offset as input, executes the query against the database to fetch the matching records, and returns the records. It supports pagination through the limit and offset parameters. If an error occurs during the operation, it logs the error and returns a dictionary containing the error details.

        Parameters:
        query (sqlalchemy.sql.selectable.Select): The SQLAlchemy query to execute.
        limit (int, optional): The maximum number of records to return. Defaults to 500.
        offset (int, optional): The number of records to skip before starting to fetch the records. Defaults to 0.

        Returns:
        list or dict: The list of matching records if the operation is successful, otherwise a dictionary containing the error details.
        """
        logger.debug("Starting read_query operation")
        try:
            async with self.async_db.get_db_session() as session:
                # Execute the fetch query with the given limit and offset
                logger.debug(
                    f"Executing fetch query: {query} with limit: {limit} and offset: {offset}"
                )
                result = await session.execute(query.limit(limit).offset(offset))
                records = result.scalars().all()

                # Convert each record to a dictionary and log it
                records_data = [record.__dict__ for record in records]
                logger.info(
                    f"Fetch query executed successfully. Records: {records_data}"
                )

                return records
        # Catch any exception that occurs during the operation
        except Exception as ex:
            # Call the handle_exceptions function to handle the exception.
            # This function checks the type of the exception and returns an appropriate error dictionary.
            # This way, we can handle multiple types of exceptions in a consistent manner across different methods.
            return handle_exceptions(ex)

    async def read_multi_query(self, queries: Dict[str, str], limit=500, offset=0):
        """
        Executes multiple fetch queries and returns the results.

        This method takes a dictionary of SQL queries, executes each query against the database to fetch the matching records, and returns a dictionary of results. Each key in the result dictionary corresponds to a query name, and the value is a list of matching records for that query. The method also supports pagination through the limit and offset parameters.

        Parameters:
        queries (Dict[str, str]): A dictionary where the key is the query name and the value is the SQL query to execute.
        limit (int, optional): The maximum number of records to return for each query. Defaults to 500.
        offset (int, optional): The number of records to skip before starting to fetch the records for each query. Defaults to 0.

        Returns:
        Dict[str, list]: A dictionary where the key is the query name and the value is a list of matching records.
        """
        logger.debug("Starting read_multi_query operation")
        try:
            results = {}
            async with self.async_db.get_db_session() as session:
                # Execute each fetch query with the given limit and offset
                for query_name, query in queries.items():
                    logger.debug(f"Executing fetch query: {query}")
                    result = await session.execute(query.limit(limit).offset(offset))
                    data = result.scalars().all()

                    # Convert each record to a dictionary and log it
                    data_dicts = [record.__dict__ for record in data]
                    logger.debug(f"Fetch result for query '{query_name}': {data_dicts}")
                    logger.info(
                        f"Fetch query executed successfully: {query_name} with {len(data)} records"
                    )

                    results[query_name] = data
            return results
        # Catch any exception that occurs during the operation
        except Exception as ex:
            # Call the handle_exceptions function to handle the exception.
            # This function checks the type of the exception and returns an appropriate error dictionary.
            # This way, we can handle multiple types of exceptions in a consistent manner across different methods.
            return handle_exceptions(ex)

    async def update_one(self, table, record_id: str, new_values: dict):
        """
        Updates a single record in the database.

        This method takes a table, a record ID, and a dictionary of new values. It fetches the record from the database using the provided ID, updates the record with the new values, and commits the session. If the operation is successful, it returns the updated record. If an error occurs during the operation, it logs the error and returns a dictionary containing the error details.

        Parameters:
        table (Table): The table in the database where the record is located.
        record_id (str): The ID of the record to update.
        new_values (dict): The new values to update the record with, represented as a dictionary where the keys are the column names and the values are the new column values.

        Returns:
        dict or dict: The record that was updated in the database if the operation is successful, otherwise a dictionary containing the error details.
        """
        non_updatable_fields = ["id", "date_created"]

        logger.debug(
            f"Starting update_one operation for record_id: {record_id} in table: {table.__name__}"
        )

        try:
            async with self.async_db.get_db_session() as session:
                # Fetch the record to be updated
                logger.debug(f"Fetching record with id: {record_id}")
                record = await session.get(table, record_id)
                if not record:
                    logger.error(f"No record found with id: {record_id}")
                    return {
                        "error": "Record not found",
                        "details": f"No record found with id {record_id}",
                    }

                # Update the record with new values
                logger.debug(f"Updating record with new values: {new_values}")
                for key, value in new_values.items():
                    if key not in non_updatable_fields:
                        setattr(record, key, value)
                await session.commit()
                logger.info(f"Record updated successfully: {record.id}")
                return record
        # Catch any exception that occurs during the operation
        except Exception as ex:
            # Call the handle_exceptions function to handle the exception.
            # This function checks the type of the exception and returns an appropriate error dictionary.
            # This way, we can handle multiple types of exceptions in a consistent manner across different methods.
            return handle_exceptions(ex)

    async def delete_one(self, table, record_id: str):
        """
        Deletes a single record from the database.

        This method takes a table and a record ID. It fetches the record from the database using the provided ID, deletes the record from the session, and commits the session. If the operation is successful, it returns a success message. If an error occurs during the operation, it logs the error and returns a dictionary containing the error details.

        Parameters:
        table (Table): The table in the database where the record is located.
        record_id (str): The ID of the record to delete.

        Returns:
        dict: A success message if the operation is successful, otherwise a dictionary containing the error details.
        """
        logger.debug(
            f"Starting delete_one operation for record_id: {record_id} in table: {table.__name__}"
        )

        try:
            async with self.async_db.get_db_session() as session:
                # Fetch the record to be deleted
                logger.debug(f"Fetching record with id: {record_id}")
                record = await session.get(table, record_id)

                # If the record doesn't exist, return an error
                if not record:
                    logger.error(f"No record found with id: {record_id}")
                    return {
                        "error": "Record not found",
                        "details": f"No record found with id {record_id}",
                    }

                # Delete the record
                logger.debug(f"Deleting record with id: {record_id}")
                await session.delete(record)
                logger.debug(f"Record deleted from session: {record}")

                # Commit the changes
                logger.debug(
                    f"Committing changes to delete record with id: {record_id}"
                )
                await session.commit()

                logger.info(f"Record deleted successfully: {record_id}")
                return {"success": "Record deleted successfully"}

        # Catch any exception that occurs during the operation
        except Exception as ex:
            # Call the handle_exceptions function to handle the exception.
            # This function checks the type of the exception and returns an appropriate error dictionary.
            # This way, we can handle multiple types of exceptions in a consistent manner across different methods.
            return handle_exceptions(ex)
