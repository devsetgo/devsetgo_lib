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


    async def get_columns_details(self, table):
        logger.debug(f"Starting get_columns_config operation for table: {table.__name__}")
        try:
            logger.debug(f"Getting columns for table: {table.__name__}")
            columns = {
                c.name: {
                    "type": str(c.type),
                    "nullable": c.nullable,
                    "primary_key": c.primary_key,
                    "unique": c.unique,
                    "autoincrement": c.autoincrement,
                    "default": str(c.default.arg) if c.default is not None and not callable(c.default.arg) else None,
                }
                for c in table.__table__.columns
            }
            logger.info(f"Columns retrieved successfully: {columns}")
            return columns
        except Exception as ex:
            logger.error(f"Exception occurred: {ex}")
            return handle_exceptions(ex)


    async def get_primary_keys(self, table):

        logger.debug(f"Starting get_primary_keys operation for table: {table.__name__}")
        try:

            logger.debug(f"Getting primary keys for table: {table.__name__}")
            primary_keys = table.__table__.primary_key.columns.keys()
            logger.info(f"Primary keys retrieved successfully: {primary_keys}")
            return primary_keys

        except Exception as ex:
            logger.error(f"Exception occurred: {ex}")
            return handle_exceptions(ex)


    async def get_one_record(self, query):

        logger.debug(
            f"Starting get_one_record operation for {query}"
        )
        try:
            async with self.async_db.get_db_session() as session:

                logger.debug(f"Getting record with query: {query}")
                result = await session.execute(query)
                record = result.scalar_one()
                logger.info(f"Record retrieved successfully: {record}")
                return record

        except Exception as ex:
            logger.error(f"Exception occurred: {ex}")
            return handle_exceptions(ex)


    async def create_one(self, record):

        logger.debug("Starting create_one operation")
        try:
            async with self.async_db.get_db_session() as session:

                logger.debug(f"Adding record to session: {record.__dict__}")
                session.add(record)
                await session.commit()
                logger.info(f"Record added successfully: {record}")
                return record

        except Exception as ex:
            logger.error(f"Exception occurred: {ex}")
            return handle_exceptions(ex)


    async def create_many(self, records):

        logger.debug("Starting create_many operation")
        try:
            t0 = time.time()
            async with self.async_db.get_db_session() as session:

                logger.debug(f"Adding {len(records)} records to session")
                session.add_all(records)
                await session.commit()
                records_data = [record.__dict__ for record in records]
                logger.debug(f"Records added to session: {records_data}")

                num_records = len(records)
                t1 = time.time() - t0
                logger.info(
                    f"Record operations were successful. {num_records} records were created in {t1:.4f} seconds."
                )
                return records

        except Exception as ex:
            logger.error(f"Exception occurred: {ex}")
            return handle_exceptions(ex)


    async def count_query(self, query):

        logger.debug("Starting count_query operation")
        try:
            async with self.async_db.get_db_session() as session:

                logger.debug(f"Executing count query: {query}")
                result = await session.execute(select(func.count()).select_from(query))
                count = result.scalar()
                logger.info(f"Count query executed successfully. Result: {count}")
                return count

        except Exception as ex:
            logger.error(f"Exception occurred: {ex}")
            return handle_exceptions(ex)


    async def read_query(self, query, limit=500, offset=0):

        logger.debug("Starting read_query operation")
        try:
            async with self.async_db.get_db_session() as session:

                logger.debug(
                    f"Executing fetch query: {query} with limit: {limit} and offset: {offset}"
                )
                result = await session.execute(query.limit(limit).offset(offset))
                records = result.scalars().all()


                records_data = [record.__dict__ for record in records]
                logger.info(
                    f"Fetch query executed successfully. Records: {records_data}"
                )

                return records

        except Exception as ex:
            logger.error(f"Exception occurred: {ex}")
            return handle_exceptions(ex)


    async def read_multi_query(self, queries: Dict[str, str], limit=500, offset=0):

        logger.debug("Starting read_multi_query operation")
        try:
            results = {}
            async with self.async_db.get_db_session() as session:

                for query_name, query in queries.items():
                    logger.debug(f"Executing fetch query: {query}")
                    result = await session.execute(query.limit(limit).offset(offset))
                    data = result.scalars().all()

                    data_dicts = [record.__dict__ for record in data]
                    logger.debug(f"Fetch result for query '{query_name}': {data_dicts}")
                    logger.info(
                        f"Fetch query executed successfully: {query_name} with {len(data)} records"
                    )

                    results[query_name] = data
            return results

        except Exception as ex:
            logger.error(f"Exception occurred: {ex}")
            return handle_exceptions(ex)


    async def update_one(self, table, record_id: str, new_values: dict):
        non_updatable_fields = ["id", "date_created"]

        logger.debug(
            f"Starting update_one operation for record_id: {record_id} in table: {table.__name__}"
        )

        try:
            async with self.async_db.get_db_session() as session:

                logger.debug(f"Fetching record with id: {record_id}")
                record = await session.get(table, record_id)
                if not record:
                    logger.error(f"No record found with id: {record_id}")
                    return {
                        "error": "Record not found",
                        "details": f"No record found with id {record_id}",
                    }

                logger.debug(f"Updating record with new values: {new_values}")
                for key, value in new_values.items():
                    if key not in non_updatable_fields:
                        setattr(record, key, value)
                await session.commit()
                logger.info(f"Record updated successfully: {record.id}")
                return record

        except Exception as ex:
            logger.error(f"Exception occurred: {ex}")
            return handle_exceptions(ex)


    async def delete_one(self, table, record_id: str):

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

        except Exception as ex:
            logger.error(f"Exception occurred: {ex}")
            return handle_exceptions(ex)
