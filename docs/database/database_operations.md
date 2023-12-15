# DatabaseOperations Module Documentation

## Purpose

The `DatabaseOperations` module provides a set of methods to interact with a database using SQLAlchemy's asynchronous API. It includes methods for creating, reading, updating, and deleting records in a database. It also includes methods for executing queries and handling exceptions.

## How to Use

### Initialization

First, you need to create an instance of the `DatabaseOperations` class. This class requires a reference to your database.

```python

from dsg_lib import (
    async_database,
    base_schema,
    database_config,
    database_operations,
)

# Create a DBConfig instance
config = {
    "database_uri": "sqlite+aiosqlite:///:memory:?cache=shared",
    "echo": False,
    "future": True,
    "pool_recycle": 3600,
}

db_config = database_config.DBConfig(config)
# Create an AsyncDatabase instance
async_db = async_database.AsyncDatabase(db_config)

# Create a DatabaseOperations instance
db_operations = database_operations.DatabaseOperations(async_db)

```

### Methods

#### `get_one_record(query)`

This method retrieves a single record from the database based on the provided query.

```python
# Get a single record
record = await db_operations.get_one_record(query)
```

#### `count_query(query)`

This method executes a count query on the database and returns the count of records that match the query.

```python
# Count records
count = await db_operations.count_query(query)
```

#### `read_query(query, limit=500, offset=0)`

This method executes a fetch query on the database and returns the records that match the query.

```python
# Read records
records = await db_operations.read_query(query)
```

#### `read_multi_query(queries: Dict[str, str], limit=500, offset=0)`

This method executes multiple fetch queries on the database and returns the records that match each query.

```python
# Read multiple queries
results = await db_operations.read_multi_query(queries)
```

#### `update_one(table, record_id: str, new_values: dict)`

This method updates a single record in the database.

```python
# Update a record
updated_record = await db_operations.update_one(User, record_id, new_values)
```

#### `delete_one(table, record_id: str)`

This method deletes a single record from the database.

```python
# Delete a record
result = await db_operations.delete_one(User, record_id)
```

### Error Handling

Each method in the `DatabaseOperations` class includes error handling. If an error occurs during the execution of a method, the method will return a dictionary with an "error" key and a description of the error.