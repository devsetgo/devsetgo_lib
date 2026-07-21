# -*- coding: utf-8 -*-
"""
This module defines the base schema for database models in the application.

The module uses SQLAlchemy as the ORM and provides a `SchemaBase` mixin class per
supported database dialect. All models should inherit from one of these classes
alongside the declarative `Base`. Each mixin provides three common columns:

- `pkid`: A unique identifier for each record. It's a string representation of a
  UUID.
- `date_created`: The date and time when a particular row was inserted into the
  table. Defaults to the current UTC time when the row is inserted.
- `date_updated`: The date and time when a particular row was last updated.
  Defaults to the current UTC time whenever the row is updated.

`SchemaBaseSQLite` sets these timestamps in Python (via `default`/`onupdate`
callables) since SQLite has no reliable server-side UTC timestamp function. Every
other dialect (`SchemaBasePostgres`, `SchemaBaseMySQL`, `SchemaBaseOracle`,
`SchemaBaseMSSQL`, `SchemaBaseFirebird`, `SchemaBaseSybase`,
`SchemaBaseCockroachDB`) sets them via a dialect-specific server-side default
expression, built by the `_build_server_default_schema_base` factory below so the
column definitions aren't repeated per dialect.

Example:
```python
from dsg_lib.async_database_functions import base_schema

class MyModel(base_schema.SchemaBaseSQLite):
        # Define your model-specific columns here
        my_column = base_schema.Column(base_schema.String(50))
```

Author: Mike Ryan
Date: 2024/05/16
License: MIT
"""

# Importing required modules from Python's standard library
import datetime
import sys
from uuid import uuid4

# Import only the SQLAlchemy components needed for this module
from .__import_sqlalchemy import Column, DateTime, String, text


def get_utc_now():
    """
    Get current UTC datetime using the appropriate method based on Python version.

    Python 3.11+ uses datetime.UTC, while earlier versions use datetime.timezone.utc.
    This prevents deprecation warnings in newer Python versions.

    Returns:
        datetime.datetime: Current UTC datetime
    """
    if sys.version_info >= (3, 11):
        return datetime.datetime.now(datetime.UTC)
    else:
        return datetime.datetime.now(datetime.timezone.utc)


# comments
uuid_comment = "Unique identifier for each record, a string representation of a UUID"
date_created_comment = (
    "Date and time when a row was inserted, defaults to current UTC time"
)
date_updated_comment = (
    "Date and time when a row was last updated, defaults to current UTC time on update"
)


def _build_pkid_column() -> Column:
    """Build a fresh `pkid` UUID-string primary key column."""
    return Column(
        String(36),
        primary_key=True,
        index=True,
        default=lambda: str(uuid4()),
        comment=uuid_comment,
    )


def _build_server_default_schema_base(
    class_name: str,
    default_expression: str,
    *,
    created_comment: str = date_created_comment,
    updated_comment: str = date_updated_comment,
) -> type:
    """
    Create a schema-base mixin class whose timestamp columns are populated by a
    dialect-specific server-side SQL expression.

    Each supported dialect (Postgres, MySQL, Oracle, MSSQL, Firebird, Sybase,
    CockroachDB) differs only in the SQL expression used to stamp the current UTC
    time, so this factory builds the common `pkid`/`date_created`/`date_updated`
    columns once per dialect instead of repeating them by hand.

    Args:
        class_name: The `__name__` to give the generated class (e.g. "SchemaBasePostgres").
        default_expression: The SQL expression (passed to `text()`) used as the
            `server_default`/`onupdate` for `date_created`/`date_updated`.
        created_comment: Column comment for `date_created`.
        updated_comment: Column comment for `date_updated`.

    Returns:
        type: A new mixin class with `pkid`, `date_created`, and `date_updated` columns.
    """
    attrs = {
        "__doc__": (
            f"Schema-base mixin providing `pkid`, `date_created`, and `date_updated` "
            f"columns, with timestamps defaulted via `{default_expression}`."
        ),
        "pkid": _build_pkid_column(),
        "date_created": Column(
            DateTime,
            index=True,
            server_default=text(default_expression),
            comment=created_comment,
        ),
        "date_updated": Column(
            DateTime,
            index=True,
            server_default=text(default_expression),
            onupdate=text(default_expression),
            comment=updated_comment,
        ),
    }
    return type(class_name, (), attrs)


class SchemaBaseSQLite:
    """
    Schema-base mixin for SQLite models.

    SQLite has no reliable server-side UTC timestamp function, so `date_created`
    and `date_updated` are stamped in Python at insert/update time instead of via
    a server-side default.

    Example:
    ```python
    from dsg_lib.async_database_functions import base_schema
    from sqlalchemy.orm import declarative_base

    BASE = declarative_base()

    class MyModel(base_schema.SchemaBaseSQLite, BASE):
        my_column = base_schema.Column(base_schema.String(50))
    ```
    """

    pkid = _build_pkid_column()

    date_created = Column(
        DateTime,
        index=True,
        default=get_utc_now,
        comment=date_created_comment,
    )

    date_updated = Column(
        DateTime,
        index=True,
        default=get_utc_now,
        onupdate=get_utc_now,
        comment=date_updated_comment,
    )


# PostgreSQL: current UTC time via `CURRENT_TIMESTAMP AT TIME ZONE 'UTC'`.
SchemaBasePostgres = _build_server_default_schema_base(
    "SchemaBasePostgres", "(CURRENT_TIMESTAMP AT TIME ZONE 'UTC')"
)

# MySQL: current UTC time via `UTC_TIMESTAMP()`.
SchemaBaseMySQL = _build_server_default_schema_base(
    "SchemaBaseMySQL", "UTC_TIMESTAMP()"
)

# Oracle: current UTC time via `SYS_EXTRACT_UTC(SYSTIMESTAMP)`.
SchemaBaseOracle = _build_server_default_schema_base(
    "SchemaBaseOracle", "SYS_EXTRACT_UTC(SYSTIMESTAMP)"
)

# Microsoft SQL Server: current UTC time via `GETUTCDATE()`.
SchemaBaseMSSQL = _build_server_default_schema_base(
    "SchemaBaseMSSQL", "GETUTCDATE()"
)

# Firebird has no built-in UTC-specific function; falls back to local
# `CURRENT_TIMESTAMP`, hence the distinct (non-UTC-worded) column comments.
SchemaBaseFirebird = _build_server_default_schema_base(
    "SchemaBaseFirebird",
    "CURRENT_TIMESTAMP",
    created_comment="Date and time when a row was inserted, defaults to current time",
    updated_comment="Date and time when a row was last updated, defaults to current time on update",
)

# Sybase: current UTC time via `GETUTCDATE()`.
SchemaBaseSybase = _build_server_default_schema_base(
    "SchemaBaseSybase", "GETUTCDATE()"
)

# CockroachDB uses PostgreSQL-compatible syntax.
SchemaBaseCockroachDB = _build_server_default_schema_base(
    "SchemaBaseCockroachDB", "(CURRENT_TIMESTAMP AT TIME ZONE 'UTC')"
)
