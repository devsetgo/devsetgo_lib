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

Example:
```python
from dsg_lib.async_database_functions import base_schema

class MyModel(base_schema.SchemaBaseSQLite):
        # Define your model-specific columns here my_column =
        base_schema.Column(base_schema.String(50))
```

Author: Mike Ryan
Date: 2024/05/16
License: MIT
"""
# TODO: change datetime.datetime.now(datetime.timezone.utc) to \
# datetime.datetime.now(datetime.UTC) once only 3.11+ is supported

# Importing required modules from Python's standard library
import datetime
from uuid import uuid4

from .__import_sqlalchemy import import_sqlalchemy

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


# comments
uuid_comment = "Unique identifier for each record, a string representation of a UUID"
date_created_comment = (
    "Date and time when a row was inserted, defaults to current UTC time"
)
date_updated_comment = (
    "Date and time when a row was last updated, defaults to current UTC time on update"
)


class SchemaBaseSQLite:
    """
    This class provides a base schema that includes common columns for most
    models. All other models should inherit from this class.

    Attributes:
        pkid (str): A unique identifier for each record. It's a string
        representation of a UUID.
        date_created (datetime): The date and time when a particular row was
        inserted into the table. It defaults to the current UTC time when the
        instance is created.
        date_updated (datetime): The date and time when a particular row was
        last updated. It defaults to the current UTC time whenever the instance
        is updated.

    Example:
    ```python
    from dsg_lib.async_database_functions import base_schema
    from sqlalchemy.orm import declarative_base

    BASE = declarative_base()

    class MyModel(base_schema.SchemaBase, BASE):
        # Define your model-specific columns here
        my_column = base_schema.Column(base_schema.String(50))
    ```
    """

    # Each instance in the table will have a unique id which is a string
    # representation of a UUID
    pkid = Column(
        String(36),
        primary_key=True,
        index=True,
        default=lambda: str(uuid4()),
        comment=uuid_comment,
    )

    # The date and time when a particular row was inserted into the table. It
    # defaults to the current UTC time when the instance is created.
    date_created = Column(
        DateTime,
        index=True,
        default=datetime.datetime.now(datetime.timezone.utc),
        comment=date_created_comment,
    )

    # The date and time when a particular row was last updated. It defaults to
    # the current UTC time whenever the instance is updated.
    date_updated = Column(
        DateTime,
        index=True,
        default=datetime.datetime.now(datetime.timezone.utc),
        onupdate=datetime.datetime.now(datetime.timezone.utc),
        comment=date_updated_comment,
    )


class SchemaBasePostgres:
    """
    This class provides a base schema that includes common columns for most
    models when using a PostgreSQL database. All other models should inherit
    from this class.

    Attributes:
        pkid (str): A unique identifier for each record. It's a string
        representation of a UUID.
        date_created (datetime): The date and time when a particular row was
        inserted into the table. It defaults to the current UTC time when the
        instance is created.
        date_updated (datetime): The date and time when a particular row was
        last updated. It defaults to the current UTC time whenever the instance
        is updated.

    Example:
    ```python
    from dsg_lib.async_database_functions import base_schema
    from sqlalchemy.orm import declarative_base

    BASE = declarative_base()

    class MyModel(base_schema.SchemaBasePostgres, BASE):
        # Define your model-specific columns here
        my_column = base_schema.Column(base_schema.String(50))
    ```
    """

    # Each instance in the table will have a unique id which is a string
    # representation of a UUID
    pkid = Column(
        String(36),
        primary_key=True,
        index=True,
        default=lambda: str(uuid4()),
        comment=uuid_comment,
    )

    # The date and time when a particular row was inserted into the table. It
    # defaults to the current UTC time when the instance is created.
    date_created = Column(
        DateTime,
        index=True,
        server_default=text("(CURRENT_TIMESTAMP AT TIME ZONE 'UTC')"),
        comment=date_created_comment,
    )

    # The date and time when a particular row was last updated. It defaults to
    # the current UTC time whenever the instance is updated.
    date_updated = Column(
        DateTime,
        index=True,
        server_default=text("(CURRENT_TIMESTAMP AT TIME ZONE 'UTC')"),
        onupdate=text("(CURRENT_TIMESTAMP AT TIME ZONE 'UTC')"),
        comment=date_updated_comment,
    )


class SchemaBaseMySQL:
    """
    This class provides a base schema that includes common columns for most
    models when using a MySQL database. All other models should inherit
    from this class.

    Attributes:
        pkid (str): A unique identifier for each record. It's a string
        representation of a UUID.
        date_created (datetime): The date and time when a particular row was
        inserted into the table. It defaults to the current UTC time when the
        instance is created.
        date_updated (datetime): The date and time when a particular row was
        last updated. It defaults to the current UTC time whenever the instance
        is updated.

    Example:
    ```python
    from dsg_lib.async_database_functions import base_schema
    from sqlalchemy.orm import declarative_base

    BASE = declarative_base()

    class MyModel(base_schema.SchemaBaseMySQL, BASE):
        # Define your model-specific columns here
        my_column = base_schema.Column(base_schema.String(50))
    ```
    """

    # Each instance in the table will have a unique id which is a string
    # representation of a UUID
    pkid = Column(
        String(36),
        primary_key=True,
        index=True,
        default=lambda: str(uuid4()),
        comment=uuid_comment,
    )

    # The date and time when a particular row was inserted into the table. It
    # defaults to the current UTC time when the instance is created.
    date_created = Column(
        DateTime,
        index=True,
        server_default=text("UTC_TIMESTAMP()"),
        comment=date_created_comment,
    )

    # The date and time when a particular row was last updated. It defaults to
    # the current UTC time whenever the instance is updated.
    date_updated = Column(
        DateTime,
        index=True,
        server_default=text("UTC_TIMESTAMP()"),
        onupdate=text("UTC_TIMESTAMP()"),
        comment=date_updated_comment,
    )


class SchemaBaseOracle:
    """
    This class provides a base schema that includes common columns for most
    models when using an Oracle database. All other models should inherit
    from this class.

    Attributes:
        pkid (str): A unique identifier for each record. It's a string
        representation of a UUID.
        date_created (datetime): The date and time when a particular row was
        inserted into the table. It defaults to the current UTC time when the
        instance is created.
        date_updated (datetime): The date and time when a particular row was
        last updated. It defaults to the current UTC time whenever the instance
        is updated.

    Example:
    ```python
    from dsg_lib.async_database_functions import base_schema
    from sqlalchemy.orm import declarative_base

    BASE = declarative_base()

    class MyModel(base_schema.SchemaBaseOracle, BASE):
        # Define your model-specific columns here
        my_column = base_schema.Column(base_schema.String(50))
    ```
    """

    # Each instance in the table will have a unique id which is a string
    # representation of a UUID
    pkid = Column(
        String(36),
        primary_key=True,
        index=True,
        default=lambda: str(uuid4()),
        comment=uuid_comment,
    )

    # The date and time when a particular row was inserted into the table. It
    # defaults to the current UTC time when the instance is created.
    date_created = Column(
        DateTime,
        index=True,
        server_default=text("SYS_EXTRACT_UTC(SYSTIMESTAMP)"),
        comment=date_created_comment,
    )

    # The date and time when a particular row was last updated. It defaults to
    # the current UTC time whenever the instance is updated.
    date_updated = Column(
        DateTime,
        index=True,
        server_default=text("SYS_EXTRACT_UTC(SYSTIMESTAMP)"),
        onupdate=text("SYS_EXTRACT_UTC(SYSTIMESTAMP)"),
        comment=date_updated_comment,
    )


class SchemaBaseMSSQL:
    """
    This class provides a base schema that includes common columns for most
    models when using a Microsoft SQL Server database. All other models should
    inherit from this class.

    Attributes:
        pkid (str): A unique identifier for each record. It's a string
        representation of a UUID.
        date_created (datetime): The date and time when a particular row was
        inserted into the table. It defaults to the current UTC time when the
        instance is created.
        date_updated (datetime): The date and time when a particular row was
        last updated. It defaults to the current UTC time whenever the instance
        is updated.

    Example:
    ```python
    from dsg_lib.async_database_functions import base_schema
    from sqlalchemy.orm import declarative_base

    BASE = declarative_base()

    class MyModel(base_schema.SchemaBaseMSSQL, BASE):
        # Define your model-specific columns here
        my_column = base_schema.Column(base_schema.String(50))
    ```
    """

    # Each instance in the table will have a unique id which is a string
    # representation of a UUID
    pkid = Column(
        String(36),
        primary_key=True,
        index=True,
        default=lambda: str(uuid4()),
        comment=uuid_comment,
    )

    # The date and time when a particular row was inserted into the table. It
    # defaults to the current UTC time when the instance is created.
    date_created = Column(
        DateTime,
        index=True,
        server_default=text("GETUTCDATE()"),
        comment=date_created_comment,
    )

    # The date and time when a particular row was last updated. It defaults to
    # the current UTC time whenever the instance is updated.
    date_updated = Column(
        DateTime,
        index=True,
        server_default=text("GETUTCDATE()"),
        onupdate=text("GETUTCDATE()"),
        comment=date_updated_comment,
    )


class SchemaBaseFirebird:
    """
    This class provides a base schema that includes common columns for most
    models when using a Firebird database. All other models should inherit
    from this class.

    Attributes:
        pkid (str): A unique identifier for each record. It's a string
        representation of a UUID.
        date_created (datetime): The date and time when a particular row was
        inserted into the table. It defaults to the current time when the
        instance is created.
        date_updated (datetime): The date and time when a particular row was
        last updated. It defaults to the current time whenever the instance
        is updated.

    Example:
    ```python
    from dsg_lib.async_database_functions import base_schema
    from sqlalchemy.orm import declarative_base

    BASE = declarative_base()

    class MyModel(base_schema.SchemaBaseFirebird, BASE):
        # Define your model-specific columns here
        my_column = base_schema.Column(base_schema.String(50))
    ```
    """

    # Each instance in the table will have a unique id which is a string
    # representation of a UUID
    pkid = Column(
        String(36),
        primary_key=True,
        index=True,
        default=lambda: str(uuid4()),
        comment=uuid_comment,
    )

    # The date and time when a particular row was inserted into the table. It
    # defaults to the current time when the instance is created.
    date_created = Column(
        DateTime,
        index=True,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="Date and time when a row was inserted, defaults to current time",
    )

    # The date and time when a particular row was last updated. It defaults to
    # the current time whenever the instance is updated.
    date_updated = Column(
        DateTime,
        index=True,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP"),
        comment="Date and time when a row was last updated, defaults to current time on update",
    )


class SchemaBaseSybase:
    """
    This class provides a base schema that includes common columns for most
    models when using a Sybase database. All other models should inherit
    from this class.

    Attributes:
        pkid (str): A unique identifier for each record. It's a string
        representation of a UUID.
        date_created (datetime): The date and time when a particular row was
        inserted into the table. It defaults to the current UTC time when the
        instance is created.
        date_updated (datetime): The date and time when a particular row was
        last updated. It defaults to the current UTC time whenever the instance
        is updated.

    Example:
    ```python
    from dsg_lib.async_database_functions import base_schema
    from sqlalchemy.orm import declarative_base

    BASE = declarative_base()

    class MyModel(base_schema.SchemaBaseSybase, BASE):
        # Define your model-specific columns here
        my_column = base_schema.Column(base_schema.String(50))
    ```
    """

    # Each instance in the table will have a unique id which is a string
    # representation of a UUID
    pkid = Column(
        String(36),
        primary_key=True,
        index=True,
        default=lambda: str(uuid4()),
        comment=uuid_comment,
    )

    # The date and time when a particular row was inserted into the table. It
    # defaults to the current UTC time when the instance is created.
    date_created = Column(
        DateTime,
        index=True,
        server_default=text("GETUTCDATE()"),
        comment=date_created_comment,
    )

    # The date and time when a particular row was last updated. It defaults to
    # the current UTC time whenever the instance is updated.
    date_updated = Column(
        DateTime,
        index=True,
        server_default=text("GETUTCDATE()"),
        onupdate=text("GETUTCDATE()"),
        comment=date_updated_comment,
    )


class SchemaBaseCockroachDB:
    """
    This class provides a base schema that includes common columns for most
    models when using a CockroachDB database. CockroachDB uses the same syntax
    as PostgreSQL. All other models should inherit from this class.

    Attributes:
        pkid (str): A unique identifier for each record. It's a string
        representation of a UUID.
        date_created (datetime): The date and time when a particular row was
        inserted into the table. It defaults to the current UTC time when the
        instance is created.
        date_updated (datetime): The date and time when a particular row was
        last updated. It defaults to the current UTC time whenever the instance
        is updated.

    Example:
    ```python
    from dsg_lib.async_database_functions import base_schema
    from sqlalchemy.orm import declarative_base

    BASE = declarative_base()

    class MyModel(base_schema.SchemaBaseCockroachDB, BASE):
        # Define your model-specific columns here
        my_column = base_schema.Column(base_schema.String(50))
    ```
    """

    # Each instance in the table will have a unique id which is a string
    # representation of a UUID
    pkid = Column(
        String(36),
        primary_key=True,
        index=True,
        default=lambda: str(uuid4()),
        comment=uuid_comment,
    )

    # The date and time when a particular row was inserted into the table. It
    # defaults to the current UTC time when the instance is created.
    date_created = Column(
        DateTime,
        index=True,
        server_default=text("(CURRENT_TIMESTAMP AT TIME ZONE 'UTC')"),
        comment=date_created_comment,
    )

    # The date and time when a particular row was last updated. It defaults to
    # the current UTC time whenever the instance is updated.
    date_updated = Column(
        DateTime,
        index=True,
        server_default=text("(CURRENT_TIMESTAMP AT TIME ZONE 'UTC')"),
        onupdate=text("(CURRENT_TIMESTAMP AT TIME ZONE 'UTC')"),
        comment=date_updated_comment,
    )
