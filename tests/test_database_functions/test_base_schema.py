# -*- coding: utf-8 -*-
import datetime
import os
from uuid import uuid4

from typing import Dict, Type, Union

import pytest
from sqlalchemy import Column, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from dsg_lib.async_database_functions.base_schema import SchemaBasePostgres, SchemaBaseSQLite


def is_postgres_available():
    """Check if PostgreSQL is available for testing."""
    import socket
    try:
        # Try to connect to the PostgreSQL service
        socket.create_connection(('postgresdbTest', 5432), timeout=2)
        return True
    except (socket.error, OSError):
        try:
            # Fallback to localhost
            socket.create_connection(('localhost', 5432), timeout=2)
            return True
        except (socket.error, OSError):
            return False


# Get the database URL from the environment variable
database_url = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@postgresdbTest:5432/dsglib_test",
    # postgres://postgres:postgres@postgresdb:5432/devsetgo_local
)

Base = declarative_base()

# Define a dictionary with the connection strings for each database
# Replace the placeholders with your actual connection details
DATABASES = {
    "sqlite": "sqlite:///:memory:",
}

# Define a dictionary with the schema base classes for each database
SCHEMA_BASES: Dict[str, Type[Union[SchemaBaseSQLite, SchemaBasePostgres]]] = {
    "sqlite": SchemaBaseSQLite,
}

# Only add PostgreSQL if it's available
if is_postgres_available():
    DATABASES["postgres"] = database_url
    SCHEMA_BASES["postgres"] = SchemaBasePostgres


# Parameterize the test function with the names of the databases
@pytest.mark.parametrize("db_name", DATABASES.keys())
def test_schema_base(db_name):
    # Get the connection string and schema base class for the current database
    connection_string = DATABASES[db_name]
    SchemaBaseClass = SCHEMA_BASES[db_name]

    # Define the User model for the current database
    class User(SchemaBaseClass, Base):  # type: ignore
        __tablename__ = f"test_table_{db_name}"
        name_first = Column(String, unique=False, index=True)

    # Set up the database engine and session factory
    engine = create_engine(connection_string)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create the schema
    Base.metadata.create_all(bind=engine)

    # Create a new database session for the test
    session = SessionLocal()

    try:
        user = User()
        user.name_first = "Test"

        # Add the instance to the session and commit it to generate id
        session.add(user)
        session.commit()

        # Assert id is a valid UUID
        assert isinstance(user.pkid, str)

        # Assert date_created and date_updated are set upon creation
        assert isinstance(user.date_created, datetime.datetime)
        assert isinstance(user.date_updated, datetime.datetime)

        # Update the instance and commit changes
        user.id = str(uuid4())
        session.commit()

        # Assert date_updated is updated after editing
        assert isinstance(user.date_updated, datetime.datetime)
    finally:
        session.close()  # Close the session after the test has been run
        # Drop all tables in the database
        Base.metadata.drop_all(bind=engine)
