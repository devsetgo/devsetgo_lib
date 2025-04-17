# fastapi_example Example

# FastAPI Example Module

This module demonstrates the use of FastAPI in conjunction with the DevSetGo Toolkit to create a fully functional API.
It includes examples of database operations, user management, and system health endpoints. The module is designed to
showcase best practices for building scalable and maintainable FastAPI applications.

## Features

- **Database Integration**:
  - Uses SQLAlchemy for ORM and database interactions.
  - Supports SQLite (in-memory) for demonstration purposes.
  - Includes models for `User` and `Address` tables with relationships.

- **API Endpoints**:
  - CRUD operations for `User` records.
  - Bulk operations for creating and deleting records.
  - System health endpoints for monitoring uptime, heap dumps, and status.
  - Robots.txt endpoint for bot management.

- **Logging**:
  - Configured using `loguru` for structured and detailed logging.
  - Logs API requests, database operations, and system events.

- **Asynchronous Operations**:
  - Fully asynchronous database operations using `asyncpg` and `aiosqlite`.
  - Asynchronous lifespan management for startup and shutdown events.

- **Configuration**:
  - Modular configuration for database, logging, and API behavior.
  - Bot management configuration for controlling access to the API.

## Usage

1. **Run the Application**:
   Use the following command to start the FastAPI application:
   ```bash
   uvicorn fastapi_example:app --host 127.0.0.1 --port 5001
   ```

2. **Access the API**:
   - OpenAPI Documentation: [http://127.0.0.1:5001/docs](http://127.0.0.1:5001/docs)
   - ReDoc Documentation: [http://127.0.0.1:5001/redoc](http://127.0.0.1:5001/redoc)

3. **Database Operations**:
   - Use the provided endpoints to perform CRUD operations on the `User` and `Address` tables.
   - Example endpoints include:
     - `/database/create-one-record`
     - `/database/get-all`
     - `/database/delete-one-record`

4. **Health Monitoring**:
   - Access system health endpoints under `/api/health`.

## Dependencies

- `FastAPI`: Web framework for building APIs.
- `SQLAlchemy`: ORM for database interactions.
- `loguru`: Logging library for structured logs.
- `tqdm`: Progress bar for bulk operations.
- `pydantic`: Data validation and settings management.
- `DevSetGo Toolkit`: Custom library for database and common utility functions.

## License
This module is licensed under the MIT License.

```python
import datetime
import secrets
import time
from contextlib import asynccontextmanager

from fastapi import Body, FastAPI, Query
from fastapi.responses import RedirectResponse
from loguru import logger
from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, ForeignKey, Select, String, and_, delete, insert, or_, update
from sqlalchemy.orm import relationship
from tqdm import tqdm

from dsg_lib.async_database_functions import (
    async_database,
    base_schema,
    database_config,
    database_operations,
)
from dsg_lib.common_functions import logging_config
from dsg_lib.fastapi_functions import default_endpoints, system_health_endpoints

config = [
    {"bot": "Bytespider", "allow": False},
    {"bot": "GPTBot", "allow": False},
    {"bot": "ClaudeBot", "allow": True},
    {"bot": "ImagesiftBot", "allow": True},
    {"bot": "CCBot", "allow": False},
    {"bot": "ChatGPT-User", "allow": True},
    {"bot": "omgili", "allow": False},
    {"bot": "Diffbot", "allow": False},
    {"bot": "Claude-Web", "allow": True},
    {"bot": "PerplexityBot", "allow": False},
]

logging_config.config_log(
    logging_level="INFO",
    log_serializer=False,
    logging_directory="log",
    log_name="log.log",
    intercept_standard_logging=False,
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

# create database configuration
db_config = database_config.DBConfig(config)
# Create an AsyncDatabase instance
async_db = async_database.AsyncDatabase(db_config)

# Create a DatabaseOperations instance
db_ops = database_operations.DatabaseOperations(async_db)


class User(base_schema.SchemaBaseSQLite, async_db.Base):
    """
    User table storing user details like first name, last name, and email
    """

    __tablename__ = "users"
    __table_args__ = {
        "comment": "User table storing user details like first name, last name, and email"
    }

    first_name = Column(String(50), unique=False, index=True)  # First name of the user
    last_name = Column(String(50), unique=False, index=True)  # Last name of the user
    email = Column(
        String(200), unique=True, index=True, nullable=True
    )  # Email of the user, must be unique
    addresses = relationship(
        "Address", order_by="Address.pkid", back_populates="user"
    )  # Relationship to the Address class


class Address(base_schema.SchemaBaseSQLite, async_db.Base):
    """
    Address table storing address details like street, city, and zip code
    """

    __tablename__ = "addresses"
    __table_args__ = {
        "comment": "Address table storing address details like street, city, and zip code"
    }

    street = Column(String(200), unique=False, index=True)  # Street of the address
    city = Column(String(200), unique=False, index=True)  # City of the address
    zip = Column(String(50), unique=False, index=True)  # Zip code of the address
    user_id = Column(
        String(36), ForeignKey("users.pkid")
    )  # Foreign key to the User table
    user = relationship(
        "User", back_populates="addresses"
    )  # Relationship to the User class


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("starting up")
    # Create the tables in the database
    await async_db.create_tables()

    create_users = True
    if create_users:
        await create_a_bunch_of_users(single_entry=2, many_entries=100)
    yield
    logger.info("shutting down")
    await async_db.disconnect()
    logger.info("database disconnected")
    print("That's all folks!")


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
    lifespan=lifespan,  # this is the replacement for the startup and shutdown events
)


@app.get("/")
async def root():
    """
    Redirect to the OpenAPI documentation.

    Example:
        GET /

    Returns:
        Redirects to /docs for interactive API documentation.
    """
    logger.info("Redirecting to OpenAPI docs")
    response = RedirectResponse(url="/docs")
    return response


# Example configuration
config = {
    "enable_status_endpoint": True,
    "enable_uptime_endpoint": True,
    "enable_heapdump_endpoint": True,
    "enable_robots_endpoint": True,
    "user_agents": [
        {"bot": "Bytespider", "allow": False},
        {"bot": "GPTBot", "allow": False},
        {"bot": "ClaudeBot", "allow": True},
        {"bot": "ImagesiftBot", "allow": True},
        {"bot": "CCBot", "allow": False},
        {"bot": "ChatGPT-User", "allow": True},
        {"bot": "omgili", "allow": False},
        {"bot": "Diffbot", "allow": False},
        {"bot": "Claude-Web", "allow": True},
        {"bot": "PerplexityBot", "allow": False},
        {"bot": "Googlebot", "allow": True},
        {"bot": "Bingbot", "allow": True},
        {"bot": "Baiduspider", "allow": False},
        {"bot": "YandexBot", "allow": False},
        {"bot": "DuckDuckBot", "allow": True},
        {"bot": "Sogou", "allow": False},
        {"bot": "Exabot", "allow": False},
        {"bot": "facebot", "allow": False},
        {"bot": "ia_archiver", "allow": False},
    ],
}

# Create and include the health router if enabled
if (
    config["enable_status_endpoint"]
    or config["enable_uptime_endpoint"]
    or config["enable_heapdump_endpoint"]
):
    health_router = system_health_endpoints.create_health_router(config)
    app.include_router(health_router, prefix="/api/health", tags=["system-health"])

# Create and include the default router if enabled
if config["enable_robots_endpoint"]:
    default_router = default_endpoints.create_default_router(config["user_agents"])
    app.include_router(default_router, prefix="", tags=["default"])


async def create_a_bunch_of_users(single_entry=0, many_entries=0):
    logger.info(f"single_entry: {single_entry}")
    await async_db.create_tables()
    # Create a list to hold the user data

    # Create a loop to generate user data

    for _ in tqdm(range(single_entry), desc="executing one"):
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


@app.get("/database/get-primary-key", tags=["Database Examples"])
async def table_primary_key():
    """
    Get the primary key(s) of the User table.

    Example:
        GET /database/get-primary-key

    Returns:
        The primary key column(s) for the User table.
    """
    logger.info("Getting primary key of User table")
    pk = await db_ops.get_primary_keys(User)
    logger.info(f"Primary key of User table: {pk}")
    return {"pk": pk}


@app.get("/database/get-column-details", tags=["Database Examples"])
async def table_column_details():
    """
    Get details about all columns in the User table.

    Example:
        GET /database/get-column-details

    Returns:
        Metadata for each column in the User table.
    """
    logger.info("Getting column details of User table")
    columns = await db_ops.get_columns_details(User)
    logger.info(f"Column details of User table: {columns}")
    return {"columns": columns}


@app.get("/database/get-tables", tags=["Database Examples"])
async def table_table_details():
    """
    List all table names in the database.

    Example:
        GET /database/get-tables

    Returns:
        A list of all table names.
    """
    logger.info("Getting table names")
    tables = await db_ops.get_table_names()
    logger.info(f"Table names: {tables}")
    return {"table_names": tables}


@app.get("/database/get-count", tags=["Database Examples"])
async def get_count():
    """
    Get the total number of User records.

    Example:
        GET /database/get-count

    Returns:
        The count of User records.
    """
    logger.info("Getting count of users")
    count = await db_ops.count_query(Select(User))
    logger.info(f"Count of users: {count}")
    return {"count": count}


@app.get("/database/get-all", tags=["Database Examples"])
async def get_all(offset: int = 0, limit: int = Query(100, le=100000, ge=1)):
    """
    Retrieve all User records with pagination.

    Example:
        GET /database/get-all?offset=0&limit=10

    Returns:
        A list of User records.
    """
    logger.info(f"Getting all users with offset {offset} and limit {limit}")
    records = await db_ops.read_query(Select(User).offset(offset).limit(limit))
    logger.info(f"Retrieved {len(records)} users")
    return {"records": records}


@app.get("/database/get-one-record", tags=["Database Examples"])
async def read_one_record(record_id: str):
    """
    Retrieve a single User record by primary key.

    Example:
        GET /database/get-one-record?record_id=some-uuid

    Returns:
        The User record with the given primary key.
    """
    logger.info(f"Reading one record with id {record_id}")
    record = await db_ops.read_one_record(Select(User).where(User.pkid == record_id))
    logger.info(f"Record with id {record_id}: {record}")
    return record


class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr


class UserCreate(UserBase):
    pass


@app.post("/database/create-one-record", status_code=201, tags=["Database Examples"])
async def create_one_record(new_user: UserCreate):
    """
    Create a new User record.

    Example:
        POST /database/create-one-record
        {
            "first_name": "Alice",
            "last_name": "Smith",
            "email": "alice@example.com"
        }

    Returns:
        The created User record.
    """
    logger.info(f"Creating one record: {new_user}")
    user = User(**new_user.dict())
    record = await db_ops.create_one(user)
    logger.info(f"Created record: {record}")
    return record


@app.post("/database/create-many-records", status_code=201, tags=["Database Examples"])
async def create_many_records(number_of_users: int = Query(100, le=1000, ge=1)):
    """
    Create multiple User records in bulk.

    Example:
        POST /database/create-many-records?number_of_users=10

    Returns:
        The number of users created and the process time.
    """
    logger.info(f"Creating {number_of_users} records")
    t0 = time.time()
    users = []
    # Create a loop to generate user data
    for i in tqdm(range(number_of_users), desc="executing many"):
        value_one = secrets.token_hex(4)
        value_two = secrets.token_hex(8)
        user = User(
            first_name=f"First{value_one}{i}{value_two}",
            last_name=f"Last{value_one}{i}{value_two}",
            email=f"user{value_one}{i}{value_two}@example.com",
        )
        logger.info(f"Created user: {user.first_name}")
        users.append(user)

    # Use db_ops to add the users to the database
    await db_ops.create_many(users)
    t1 = time.time()
    process_time = format(t1 - t0, ".4f")
    logger.info(f"Created {number_of_users} records in {process_time} seconds")
    return {"number_of_users": number_of_users, "process_time": process_time}


@app.put("/database/update-one-record", status_code=200, tags=["Database Examples"])
async def update_one_record(
    id: str = Body(
        ...,
        description="UUID to update",
        examples=["6087cce8-0bdd-48c2-ba96-7d557dae843e"],
    ),
    first_name: str = Body(..., examples=["Agent"]),
    last_name: str = Body(..., examples=["Smith"]),
    email: str = Body(..., examples=["jim@something.com"]),
):
    """
    Update a User record by primary key.

    Example:
        PUT /database/update-one-record
        {
            "id": "some-uuid",
            "first_name": "Agent",
            "last_name": "Smith",
            "email": "jim@something.com"
        }

    Returns:
        The updated User record.
    """
    logger.info(f"Updating one record with id {id}")
    # adding date_updated to new_values as it is not supported in sqlite \
    # and other database may not either.
    new_values = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "date_updated": datetime.datetime.now(datetime.timezone.utc),
    }
    record = await db_ops.update_one(table=User, record_id=id, new_values=new_values)
    logger.info(f"Updated record with id {id}")
    return record


@app.delete("/database/delete-one-record", status_code=200, tags=["Database Examples"])
async def delete_one_record(record_id: str = Body(...)):
    """
    Delete a User record by primary key.

    Example:
        DELETE /database/delete-one-record
        {
            "record_id": "some-uuid"
        }

    Returns:
        Success message or error.
    """
    logger.info(f"Deleting one record with id {record_id}")
    record = await db_ops.delete_one(table=User, record_id=record_id)
    logger.info(f"Deleted record with id {record_id}")
    return record


@app.delete(
    "/database/delete-many-records-aka-this-is-a-bad-idea",
    status_code=201,
    tags=["Database Examples"],
)
async def delete_many_records(
    id_values: list = Body(...), id_column_name: str = "pkid"
):
    """
    Delete multiple User records by a list of primary keys.

    Example:
        DELETE /database/delete-many-records-aka-this-is-a-bad-idea
        {
            "id_values": ["uuid1", "uuid2", "uuid3"]
        }

    Returns:
        The number of records deleted.
    """
    logger.info(f"Deleting many records with ids {id_values}")
    record = await db_ops.delete_many(
        table=User, id_column_name="pkid", id_values=id_values
    )
    logger.info(f"Deleted records with ids {id_values}")
    return record


@app.get(
    "/database/get-list-of-records-to-paste-into-delete-many-records",
    tags=["Database Examples"],
)
async def read_list_of_records(
    offset: int = Query(0, le=1000, ge=0), limit: int = Query(100, le=10000, ge=1)
):
    """
    Get a list of User primary keys for use in bulk delete.

    Example:
        GET /database/get-list-of-records-to-paste-into-delete-many-records?offset=0&limit=10

    Returns:
        A list of User primary keys.
    """
    logger.info(f"Reading list of records with offset {offset} and limit {limit}")
    records = await db_ops.read_query(Select(User), offset=offset, limit=limit)
    records_list = []
    for record in records:
        records_list.append(record.pkid)
    logger.info(f"Read list of records: {records_list}")
    return records_list


@app.get("/database/get-list-of-distinct-records", tags=["Database Examples"])
async def read_list_of_distinct_records():
    """
    Insert many similar User records and return distinct last names.

    Example:
        GET /database/get-list-of-distinct-records

    Returns:
        A list of distinct last names.
    """
    # create many similar records to test distinct
    queries = []
    for i in tqdm(range(100), desc="executing many fake users"):
        value = f"Agent {i}"
        queries.append(
            (
                insert(User),
                {
                    "first_name": value,
                    "last_name": "Smith",
                    "email": f"{value.lower()}@abc.com",
                },
            )
        )

    results = await db_ops.execute_many(queries)
    print(results)

    distinct_last_name_query = Select(User.last_name).distinct()
    logger.info(f"Executing query: {distinct_last_name_query}")
    records = await db_ops.read_query(query=distinct_last_name_query)

    logger.info(f"Read list of distinct records: {records}")
    return records


@app.post("/database/execute-one", tags=["Database Examples"])
async def execute_query(query: str = Body(...)):
    """
    Example of running a single SQL query (insert) using execute_one.

    Example:
        POST /database/execute-one
        {
            "query": "insert example (not used, see code)"
        }

    Returns:
        The inserted User record(s) with first_name "John".
    """
    # add a user with execute_one
    logger.info(f"Executing query: {query}")

    query = insert(User).values(first_name="John", last_name="Doe", email="x@abc.com")
    result = await db_ops.execute_one(query)
    logger.info(f"Executed query: {result}")
    query_return = await db_ops.read_query(
        Select(User).where(User.first_name == "John")
    )
    return query_return


@app.post("/database/execute-many", tags=["Database Examples"])
async def execute_many(query: str = Body(...)):
    """
    Example of running multiple SQL queries (bulk insert) using execute_many.

    Example:
        POST /database/execute-many
        {
            "query": "bulk insert example (not used, see code)"
        }

    Returns:
        All User records after bulk insert.
    """
    # multiple users with execute_many
    logger.info(f"Executing query: {query}")
    queries = []

    for i in range(10):
        query = insert(User).values(
            first_name=f"User{i}", last_name="Doe", email="x@abc.com"
        )
        queries.append(query)

    results = await db_ops.execute_many(queries)
    logger.info(f"Executed query: {results}")
    query_return = await db_ops.read_query(Select(User))
    return query_return


@app.get("/database/get-distinct-emails", tags=["Database Examples"])
async def get_distinct_emails():
    """
    Get a list of distinct emails from the User table.

    Example:
        GET /database/get-distinct-emails

    Returns:
        A list of unique email addresses.
    """
    from sqlalchemy import select

    query = select(User.email).distinct()
    logger.info("Getting distinct emails")
    records = await db_ops.read_query(query)
    return {"distinct_emails": records}


@app.get("/database/get-users-by-email", tags=["Database Examples"])
async def get_users_by_email(email: str):
    """
    Get User records by email address.

    Example:
        GET /database/get-users-by-email?email=alice@example.com

    Returns:
        A list of User records matching the email.
    """
    query = Select(User).where(User.email == email)
    logger.info(f"Getting users with email: {email}")
    records = await db_ops.read_query(query)
    return {"users": records}


@app.get("/database/get-users-by-name", tags=["Database Examples"])
async def get_users_by_name(first_name: str = "", last_name: str = ""):
    """
    Get User records by first and/or last name.

    Example:
        GET /database/get-users-by-name?first_name=Alice&last_name=Smith

    Returns:
        A list of User records matching the name.
    """
    filters = []
    if first_name:
        filters.append(User.first_name == first_name)
    if last_name:
        filters.append(User.last_name == last_name)
    query = Select(User).where(and_(*filters)) if filters else Select(User)
    logger.info(f"Getting users by name: {first_name} {last_name}")
    records = await db_ops.read_query(query)
    return {"users": records}


@app.get("/database/get-users-or", tags=["Database Examples"])
async def get_users_or(first_name: str = "", last_name: str = ""):
    """
    Get User records where first name OR last name matches.

    Example:
        GET /database/get-users-or?first_name=Alice

    Returns:
        A list of User records matching either name.
    """
    filters = []
    if first_name:
        filters.append(User.first_name == first_name)
    if last_name:
        filters.append(User.last_name == last_name)
    query = Select(User).where(or_(*filters)) if filters else Select(User)
    logger.info(f"Getting users by OR: {first_name} {last_name}")
    records = await db_ops.read_query(query)
    return {"users": records}


@app.get("/database/get-multi-query", tags=["Database Examples"])
async def get_multi_query():
    """
    Run multiple queries at once and return results as a dictionary.

    Example:
        GET /database/get-multi-query

    Returns:
        A dictionary with results for each query.
    """
    queries = {
        "all_users": Select(User),
        "distinct_emails": Select(User.email).distinct(),
        "first_10": Select(User).limit(10),
    }
    logger.info("Running multi-query example")
    results = await db_ops.read_multi_query(queries)
    return results


@app.put("/database/update-email", tags=["Database Examples"])
async def update_email(record_id: str = Body(...), new_email: str = Body(...)):
    """
    Update a User's email address by primary key.

    Example:
        PUT /database/update-email
        {
            "record_id": "some-uuid",
            "new_email": "new@email.com"
        }

    Returns:
        Result of the update operation.
    """
    query = update(User).where(User.pkid == record_id).values(email=new_email)
    logger.info(f"Updating email for user {record_id} to {new_email}")
    result = await db_ops.execute_one(query)
    return {"result": result}


@app.delete("/database/delete-by-email", tags=["Database Examples"])
async def delete_by_email(email: str = Body(...)):
    """
    Delete User records by email address.

    Example:
        DELETE /database/delete-by-email
        {
            "email": "alice@example.com"
        }

    Returns:
        Result of the delete operation.
    """
    query = delete(User).where(User.email == email)
    logger.info(f"Deleting users with email {email}")
    result = await db_ops.execute_one(query)
    return {"result": result}


@app.post("/database/insert-bulk", tags=["Database Examples"])
async def insert_bulk(count: int = Body(5)):
    """
    Bulk insert User records using execute_many.

    Example:
        POST /database/insert-bulk
        {
            "count": 10
        }

    Returns:
        Result of the bulk insert operation.
    """
    queries = []
    for i in range(count):
        value = secrets.token_hex(4)
        q = (
            insert(User),
            {
                "first_name": f"Bulk{value}{i}",
                "last_name": f"User{value}{i}",
                "email": f"bulk{value}{i}@example.com",
            },
        )
        queries.append(q)
    logger.info(f"Bulk inserting {count} users")
    result = await db_ops.execute_many(queries)
    return {"result": result}


@app.get("/database/error-example", tags=["Database Examples"])
async def error_example():
    """
    Trigger an error to demonstrate error handling.

    Example:
        GET /database/error-example

    Returns:
        Error details from a failed query.
    """
    # Try to select from a non-existent table
    from sqlalchemy import text

    query = text("SELECT * FROM non_existent_table")
    logger.info("Triggering error example")
    result = await db_ops.read_query(query)
    return {"result": result}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=5001)
```
