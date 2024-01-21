# -*- coding: utf-8 -*-
"""
This module defines the base schema for database models in the application.

The module uses SQLAlchemy as the ORM and provides a `SchemaBase` class that all
other models should inherit from. The `SchemaBase` class includes common columns
that are needed for most models like `pkid`, `date_created`, and `date_updated`.

- `pkid`: A unique identifier for each record. It's a string representation of a
  UUID.
- `date_created`: The date and time when a particular row was inserted into the
  table.
    It defaults to the current UTC time when the instance is created.
- `date_updated`: The date and time when a particular row was last updated.
    It defaults to the current UTC time whenever the instance is updated.

To create a new database model, import this module and extend the `SchemaBase`
class.

Example: ```python from dsg_lib import base_schema

class MyModel(base_schema.SchemaBase):
        # Define your model-specific columns here my_column =
        base_schema.Column(base_schema.String(50))
```
"""
# Importing required modules from Python's standard library
import datetime
from typing import Tuple
from uuid import uuid4

from packaging import version as packaging_version


def import_sqlalchemy() -> Tuple:
    """
    This function tries to import SQLAlchemy and its components, and raises an
    ImportError if SQLAlchemy is not installed or if the installed version is
    not compatible with the minimum required version.

    Returns:
        Tuple: A tuple containing the imported SQLAlchemy module and its
        components (Column, DateTime, String).

    Raises:
        ImportError: If SQLAlchemy is not installed or if the installed version
        is not compatible with the minimum required version.

    Example: ```python from dsg_lib import base_schema sqlalchemy, Column,
    DateTime, String = base_schema.import_sqlalchemy() ```
    """
    try:
        import sqlalchemy
        from sqlalchemy import Column, DateTime, String

    except ImportError:
        Column = DateTime = String = sqlalchemy = None

    # Check SQLAlchemy version
    min_version = "1.4.0"  # replace with your minimum required version
    if sqlalchemy is not None and packaging_version.parse(
        sqlalchemy.__version__
    ) < packaging_version.parse(min_version):
        raise ImportError(
            f"SQLAlchemy version >= {min_version} required, run `pip install --upgrade sqlalchemy`"
        )

    return (
        sqlalchemy,
        Column,
        DateTime,
        String,
    )


# Call the function at the module level to import SQLAlchemy and its components
(
    sqlalchemy,
    Column,
    DateTime,
    String,
) = import_sqlalchemy()


class SchemaBase:
    """
    This class provides a base schema that includes common columns for most
    models. All other models should inherit from this class.

    Attributes:
        pkid (str): A unique identifier for each record. It's a string
        representation of a UUID. date_created (datetime): The date and time
        when a particular row was inserted into the table.
            It defaults to the current UTC time when the instance is created.
        date_updated (datetime): The date and time when a particular row was
        last updated.
            It defaults to the current UTC time whenever the instance is
            updated.

    Example: ```python from dsg_lib import base_schema from sqlalchemy.orm
    import declarative_base

    BASE = declarative_base()

    class MyModel(base_schema.SchemaBase, BASE):
        # Define your model-specific columns here my_column =
        base_schema.Column(base_schema.String(50))
    ```
    """

    # TODO: change datetime.datetime.now(datetime.timezone.utc) to \
    # datetime.datetime.now(datetime.UTC) once only 3.11+ is supported

    # Each instance in the table will have a unique id which is a string
    # representation of a UUID
    pkid = Column(
        String(36),
        primary_key=True,
        index=True,
        default=lambda: str(uuid4()),
    )

    # The date and time when a particular row was inserted into the table. It
    # defaults to the current UTC time when the instance is created.
    date_created = Column(
        DateTime, index=True, default=datetime.datetime.now(datetime.timezone.utc)
    )

    # The date and time when a particular row was last updated. It defaults to
    # the current UTC time whenever the instance is updated.
    date_updated = Column(
        DateTime,
        index=True,
        default=datetime.datetime.now(datetime.timezone.utc),
        onupdate=datetime.datetime.now(datetime.timezone.utc),
    )
