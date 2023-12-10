# Database Configuration Module

This module, `database_config.py`, is designed to handle asynchronous database operations using SQLAlchemy and asyncio. It contains several classes that each play a specific role in managing and interacting with the database.

## Classes

### DBConfig

This class is responsible for managing the database configuration. It initializes the database configuration and creates a SQLAlchemy engine and a MetaData instance. The configuration is passed as a dictionary and includes parameters such as the database URI, pool size, and timeout settings. The class also provides a method to get a new database session.

#### Attributes

- `config`: A dictionary containing the database configuration.
- `engine`: The SQLAlchemy engine created with the database URI from the config.
- `metadata`: The SQLAlchemy MetaData instance.

#### Methods

- `get_db_session()`: Returns a context manager that provides a new database session.

#### Example of Use

```python
config = {
    "database_uri": "postgresql+asyncpg://user:password@localhost/dbname",
    "echo": True,
    "future": True,
    "pool_pre_ping": True,
    "pool_size": 5,
    "max_overflow": 10,
    "pool_recycle": 3600,
    "pool_timeout": 30,
}

db_config = DBConfig(config)
```

This will create a new DBConfig instance with a SQLAlchemy engine configured according to the parameters in the config dictionary.

#### Supported Features by Database

| Option | SQLite | PostgreSQL | MySQL | Oracle | MSSQL |
|--------|--------|------------|-------|--------|-------|
| echo | Yes | Yes | Yes | Yes | Yes |
| future | Yes | Yes | Yes | Yes | Yes |
| pool_pre_ping | Yes | Yes | Yes | Yes | Yes |
| pool_size | No | Yes | Yes | Yes | Yes |
| max_overflow | No | Yes | Yes | Yes | Yes |
| pool_recycle | Yes | Yes | Yes | Yes | Yes |
| pool_timeout | No | Yes | Yes | Yes | Yes |

## Constants

- `SUPPORTED_PARAMETERS`: A dictionary that specifies the supported parameters for different types of databases. This helps in validating the configuration parameters passed to the DBConfig class.

## Dependencies

The module uses the logger from the `dsg_lib` for logging. The logging helps in tracking the flow of operations and in debugging by providing useful information about the operations being performed and any errors that occur.

The module also uses the `time` module to work with times, the `contextlib` module for creating context managers, and the `typing` module for type hinting. It uses several components from the `sqlalchemy` package for database operations and error handling.

## Base Variable

The `BASE` variable is a base class for declarative database models. It is created using the `declarative_base` function from `sqlalchemy.orm`.
