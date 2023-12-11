# Base Schema Module

This module, `base_schema.py`, is designed to provide a base schema for all database models in your application. It uses SQLAlchemy as the Object-Relational Mapping (ORM) tool.

## Purpose

The purpose of this module is to define a base schema that can be inherited by all other database models in your application. This base schema includes common columns that are needed for most models, such as `pkid`, `date_created`, and `date_updated`.

- `pkid`: A unique identifier for each record. It's a string representation of a UUID.
- `date_created`: The date and time when a particular row was inserted into the table. It defaults to the current UTC time when the instance is created.
- `date_updated`: The date and time when a particular row was last updated. It defaults to the current UTC time whenever the instance is updated.

## How to Use

To use this module, you need to import it and then extend the `SchemaBase` class to create a new database model. Here's an example:

```python
from base_schema import SchemaBase
from sqlalchemy import Column, Integer, String

class User(SchemaBase):
    __tablename__ = 'users'

    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
```

In this example, the `User` model inherits from `SchemaBase`, which means it automatically includes the `pkid`, `date_created`, and `date_updated` columns. It also defines additional columns `name` and `age`.

## Dependencies

This module depends on several Python packages, including:

- `datetime` from Python's standard library for handling date and time related tasks.
- `uuid` from Python's standard library for generating unique identifiers.
- `packaging` for comparing SQLAlchemy version.
- `sqlalchemy` for defining database schema.

## Note

This module also includes a function `import_sqlalchemy` that checks the installed version of SQLAlchemy and raises an ImportError if SQLAlchemy is not installed or if the installed version is not compatible with the minimum required version.