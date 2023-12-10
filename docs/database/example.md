# Examples
Here are a few examples of how to use the database functions


## FastAPI

```python
# -*- coding: utf-8 -*-

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from loguru import logger
from tqdm import tqdm

from dsg_lib import logging_config

logging_config.config_log(
    logging_level="Debug", log_serializer=False, log_name="log.log"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("starting up")
    # Create the tables in the database
    await async_db.create_tables()

    create_users = True
    if create_users:
        await create_a_bunch_of_users(single_entry=23, many_entries=100)
    yield
    logger.info("shutting down")


# Create an instance of the FastAPI class
app = FastAPI(
    title="FastAPI Example",  # The title of the API
    description="This is an example of a FastAPI application using the DevSetGo Toolkit.",  # A brief description of the API
    version="0.1.0",  # The version of the API
    docs_url="/docs",  # The URL where the API documentation will be served
    redoc_url="/redoc",  # The URL where the ReDoc documentation will be served
    openapi_url="/openapi.json",  # The URL where the OpenAPI schema will be served
    debug=True,  # Enable debug mode
    middleware=[],  # A list of middleware to include in the application
    routes=[],  # A list of routes to include in the application
    lifespan=lifespan,
)


@app.get("/")
async def root():
    """
    Root endpoint of API
    Returns:
        Redrects to openapi document
    """
    # redirect to openapi docs
    logger.info("Redirecting to OpenAPI docs")
    response = RedirectResponse(url="/docs")
    return response

from sqlalchemy import Column, Delete, Select, String, Update

from dsg_lib.database import (
    async_database,
    base_schema,
    database_config,
    database_operations,
)

# Create a DBConfig instance
config = {
    # "database_uri": "postgresql+asyncpg://postgres:postgres@postgresdb/postgres",
    "database_uri": "sqlite+aiosqlite:///:memory:?cache=shared",
    "echo": False,
    "future": True,
    # "pool_pre_ping": True,
    # "pool_size": 10,
    # "max_overflow": 10,
    "pool_recycle": 3600,
    # "pool_timeout": 30,
}

db_config = database_config.DBConfig(config)
# Create an AsyncDatabase instance
async_db = async_database.AsyncDatabase(db_config)

# Create a DatabaseOperations instance
db_ops = database_operations.DatabaseOperations(async_db)


# User class inherits from SchemaBase and async_db.Base
# This class represents the User table in the database
class User(base_schema.SchemaBase, async_db.Base):
    __tablename__ = "users"  # Name of the table in the database

    # Define the columns of the table
    first_name = Column(String, unique=False, index=True)  # First name of the user
    last_name = Column(String, unique=False, index=True)  # Last name of the user
    email = Column(
        String, unique=True, index=True, nullable=True
    )  # Email of the user, must be unique

async def create_a_bunch_of_users(single_entry=0, many_entries=0):
    logger.info(f"single_entry: {single_entry}")
    await async_db.create_tables()
    # Create a list to hold the user data

    # Create a loop to generate user data

    for i in tqdm(range(single_entry), desc="executing one"):
        value = secrets.token_hex(16)
        user = User(
            first_name=f"First{value}",
            last_name=f"Last{value}",
            email=f"user{value}@example.com",
        )
        logger.info(f"created_users: {user}")
        await db_ops.create_one(user)

    users = []
    # Create a loop to generate user data
    for i in tqdm(range(many_entries), desc="executing many"):
        value_one = secrets.token_hex(4)
        value_two = secrets.token_hex(8)
        user = User(
            first_name=f"First{value_one}{i}{value_two}",
            last_name=f"Last{value_one}{i}{value_two}",
            email=f"user{value_one}{i}{value_two}@example.com",
        )
        logger.info(f"created_users: {user.first_name}")
        users.append(user)

    # Use db_ops to add the users to the database
    await db_ops.create_many(users)


@app.get("/database/get-count")
async def get_count():
    count = await db_ops.count_query(Select(User))
    return {"count": count}


# endpoint to get list of user
@app.get("/database/get-all")
async def get_all(offset: int = 0, limit: int = 100):
    records = await db_ops.read_query(Select(User).offset(offset).limit(limit))
    return {"records": records}


@app.get("/database/get-primary-key")
async def table_primary_key():
    pk = await db_ops.get_primary_keys(User)
    return {"pk": pk}


@app.get("/database/get-column-details")
async def table_column_details():
    columns = await db_ops.get_columns_details(User)
    return {"columns": columns}


@app.get("/database/get-tables")
async def table_table_details():
    tables = await db_ops.get_table_names()
    return {"table_names": tables}


@app.get("/database/get-one-record")
async def get_one_record(record_id: str):
    record = await db_ops.get_one_record(Select(User).where(User.pkid == record_id))
    return {"record": record}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=5000)
```

# Async Script

```python
#TODO: Create a script example

```