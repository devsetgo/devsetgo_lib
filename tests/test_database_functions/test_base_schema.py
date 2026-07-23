# -*- coding: utf-8 -*-
import datetime
import os
from uuid import uuid4

from typing import Dict, Type, Union

import pytest
from sqlalchemy import Column, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from dsg_lib.async_database_functions import base_schema
from dsg_lib.async_database_functions.base_schema import (
    SchemaBaseMSSQL,
    SchemaBasePostgres,
    SchemaBaseSQLite,
)


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


def is_mssql_available():
    """Check if SQL Server is available for testing."""
    import socket
    try:
        # Try to connect to the SQL Server service
        socket.create_connection(('mssqldbTest', 1433), timeout=2)
        return True
    except (socket.error, OSError):
        try:
            # Fallback to localhost
            socket.create_connection(('localhost', 1433), timeout=2)
            return True
        except (socket.error, OSError):
            return False


# Get the database URL from the environment variable
database_url = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@postgresdbTest:5432/dsglib_test",
    # postgres://postgres:postgres@postgresdb:5432/devsetgo_local
)

# Get the SQL Server URL from the environment variable. `TrustServerCertificate`
# is required because ODBC Driver 18 defaults to encrypted connections with
# strict certificate validation, which the test container's self-signed cert
# won't satisfy otherwise.
mssql_url = os.getenv(
    "MSSQL_URL",
    "mssql+pyodbc://sa:DevSetGo_Test1@mssqldbTest:1433/master"
    "?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes",
)

Base = declarative_base()

# Define a dictionary with the connection strings for each database
# Replace the placeholders with your actual connection details
DATABASES = {
    "sqlite": "sqlite:///:memory:",
}

# Define a dictionary with the schema base classes for each database
SCHEMA_BASES: Dict[str, Type[Union[SchemaBaseSQLite, SchemaBasePostgres, SchemaBaseMSSQL]]] = {
    "sqlite": SchemaBaseSQLite,
}

# Only add PostgreSQL if it's available
if is_postgres_available():
    DATABASES["postgres"] = database_url
    SCHEMA_BASES["postgres"] = SchemaBasePostgres

# Only add SQL Server if it's available
if is_mssql_available():
    DATABASES["mssql"] = mssql_url
    SCHEMA_BASES["mssql"] = SchemaBaseMSSQL


# Parameterize the test function with the names of the databases
@pytest.mark.parametrize("db_name", DATABASES.keys())
def test_schema_base(db_name):
    # Get the connection string and schema base class for the current database
    connection_string = DATABASES[db_name]
    SchemaBaseClass = SCHEMA_BASES[db_name]

    # Define the User model for the current database
    class User(SchemaBaseClass, Base):  # type: ignore
        __tablename__ = f"test_table_{db_name}"
        # Bounded length: SQL Server compiles unbounded `String` to
        # VARCHAR(max), which can't be used as an indexed column.
        name_first = Column(String(255), unique=False, index=True)

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


# Every server-default-backed dialect built by
# base_schema._build_server_default_schema_base, mapped to its expected
# timestamp default/onupdate SQL expression and column comments. These don't
# need a live connection: they verify the factory produced the correct,
# distinct column definitions per dialect (not just that the module imports).
SERVER_DEFAULT_DIALECTS = {
    "SchemaBasePostgres": (
        "(CURRENT_TIMESTAMP AT TIME ZONE 'UTC')",
        base_schema.date_created_comment,
        base_schema.date_updated_comment,
    ),
    "SchemaBaseMySQL": (
        "UTC_TIMESTAMP()",
        base_schema.date_created_comment,
        base_schema.date_updated_comment,
    ),
    "SchemaBaseOracle": (
        "SYS_EXTRACT_UTC(SYSTIMESTAMP)",
        base_schema.date_created_comment,
        base_schema.date_updated_comment,
    ),
    "SchemaBaseMSSQL": (
        "GETUTCDATE()",
        base_schema.date_created_comment,
        base_schema.date_updated_comment,
    ),
    "SchemaBaseFirebird": (
        "CURRENT_TIMESTAMP",
        "Date and time when a row was inserted, defaults to current time",
        "Date and time when a row was last updated, defaults to current time on update",
    ),
    "SchemaBaseSybase": (
        "GETUTCDATE()",
        base_schema.date_created_comment,
        base_schema.date_updated_comment,
    ),
    "SchemaBaseCockroachDB": (
        "(CURRENT_TIMESTAMP AT TIME ZONE 'UTC')",
        base_schema.date_created_comment,
        base_schema.date_updated_comment,
    ),
}


@pytest.mark.parametrize(
    "class_name,expected", SERVER_DEFAULT_DIALECTS.items(), ids=list(SERVER_DEFAULT_DIALECTS)
)
def test_server_default_schema_base_columns(class_name, expected):
    default_expression, created_comment, updated_comment = expected
    schema_class = getattr(base_schema, class_name)

    # The factory must preserve the intended class name (it's built via
    # type(class_name, ...), not left as the literal "SchemaBase").
    assert schema_class.__name__ == class_name

    # pkid: same UUID-string primary key across every dialect.
    assert schema_class.pkid.primary_key is True
    assert schema_class.pkid.index is True
    assert schema_class.pkid.comment == base_schema.uuid_comment

    # date_created: dialect-specific server_default, no onupdate.
    assert schema_class.date_created.index is True
    assert schema_class.date_created.comment == created_comment
    assert str(schema_class.date_created.server_default.arg) == default_expression
    assert schema_class.date_created.onupdate is None

    # date_updated: same server_default expression, plus a matching onupdate.
    assert schema_class.date_updated.index is True
    assert schema_class.date_updated.comment == updated_comment
    assert str(schema_class.date_updated.server_default.arg) == default_expression
    assert str(schema_class.date_updated.onupdate.arg) == default_expression


def test_server_default_schema_base_columns_are_independent_instances():
    # Each generated class must get its own Column objects (SQLAlchemy Columns
    # are single-use once attached to a table), not shared references from a
    # single factory call reused across dialects.
    assert (
        base_schema.SchemaBasePostgres.pkid
        is not base_schema.SchemaBaseMySQL.pkid
    )
    assert (
        base_schema.SchemaBasePostgres.date_created
        is not base_schema.SchemaBaseCockroachDB.date_created
    )


def test_sqlite_schema_base_uses_python_side_defaults():
    # SQLite has no server_default; date_created/date_updated are populated by
    # a Python callable instead (get_utc_now), including on update. SQLAlchemy
    # wraps the callable (via functools.wraps) rather than storing it as-is,
    # so compare against `.__wrapped__` rather than the wrapper itself.
    schema = base_schema.SchemaBaseSQLite
    assert schema.pkid.comment == base_schema.uuid_comment
    assert schema.date_created.default.arg.__wrapped__ is base_schema.get_utc_now
    assert schema.date_updated.default.arg.__wrapped__ is base_schema.get_utc_now
    assert schema.date_updated.onupdate.arg.__wrapped__ is base_schema.get_utc_now
