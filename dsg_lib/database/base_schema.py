# -*- coding: utf-8 -*-

"""
This module defines the base schema for database models in the application.

It uses SQLAlchemy as the ORM and provides a `SchemaBase` class that all other models should inherit from.
The `SchemaBase` class includes common columns that are needed for most models like `id`, `date_created`, and `date_updated`.

- `id`: A unique identifier for each record. It's a string representation of a UUID.
- `date_created`: The date and time when a particular row was inserted into the table.
  It defaults to the current UTC time when the instance is created.
- `date_updated`: The date and time when a particular row was last updated.
  It defaults to the current UTC time whenever the instance is updated.

Import this module and extend the `SchemaBase` class to create new database models.
"""

# Importing required modules from Python's standard library
from datetime import datetime  # For handling date and time related tasks
from uuid import uuid4  # For generating unique identifiers

# Importing required modules from SQLAlchemy for defining database schema
from sqlalchemy import Column, DateTime, String


# Defining a base class for all our database schemas
class SchemaBase:
    # Each instance in the table will have a unique id which is a string representation of a UUID
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid4()))

    # The date and time when a particular row was inserted into the table.
    # It defaults to the current UTC time when the instance is created.
    date_created = Column(DateTime, index=True, default=datetime.utcnow())

    # The date and time when a particular row was last updated.
    # It defaults to the current UTC time whenever the instance is updated.
    date_updated = Column(
        DateTime,
        index=True,
        default=datetime.utcnow(),
        onupdate=datetime.utcnow(),
    )
