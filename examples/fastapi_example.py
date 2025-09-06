# -*- coding: utf-8 -*-
"""
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
"""
import datetime
import secrets
import time
from contextlib import asynccontextmanager

from fastapi import Body, FastAPI, Query
from fastapi.responses import RedirectResponse
from loguru import logger
from pydantic import BaseModel, EmailStr
from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    and_,
    asc,
    delete,
    desc,
    func,
    insert,
    or_,
    select,
    text,
    update,
)
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
    intercept_standard_logging=True,
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


# Pydantic Models for API
class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr


class UserCreate(UserBase):
    pass


# ===================================================================
# CURRENT/RECOMMENDED DATABASE OPERATIONS
# Using execute_one, execute_many, read_query, etc.
# ===================================================================

# Database Metadata and Utility Operations
@app.get("/database/get-primary-key", tags=["Current - Database Metadata"])
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


@app.get("/database/get-column-details", tags=["Current - Database Metadata"])
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


@app.get("/database/get-tables", tags=["Current - Database Metadata"])
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


@app.get("/database/get-count", tags=["Current - Database Metadata"])
async def get_count():
    """
    Get the total number of User records using count_query.

    Example:
        GET /database/get-count

    Returns:
        The count of User records.
    """
    logger.info("Getting count of users")
    count = await db_ops.count_query(select(User))
    logger.info(f"Count of users: {count}")
    return {"count": count}


# SELECT Operations - Simple to Complex
@app.get("/database/select-simple", tags=["Current - SELECT Operations"])
async def select_simple(limit: int = Query(10, le=100, ge=1)):
    """
    Simple SELECT: Get all users with basic pagination.

    Example:
        GET /database/select-simple?limit=5

    Returns:
        A list of User records.
    """
    logger.info(f"Simple SELECT with limit {limit}")
    query = select(User).limit(limit)
    records = await db_ops.execute_one(query)
    logger.info(f"Retrieved {len(records)} users")
    return {"records": records, "query_type": "Simple SELECT with LIMIT", "query": str(query)}


@app.get("/database/select-moderate", tags=["Current - SELECT Operations"])
async def select_moderate(
    first_name: str = Query(None, description="Filter by first name"),
    email_domain: str = Query(None, description="Filter by email domain (e.g., 'example.com')")
):
    """
    Moderate SELECT: Filter users by multiple conditions with ordering.

    Example:
        GET /database/select-moderate?first_name=John&email_domain=example.com

    Returns:
        Filtered and ordered User records.
    """
    logger.info(f"Moderate SELECT with filters: {first_name}, {email_domain}")

    query = select(User)

    # Add conditional filters
    if first_name:
        query = query.where(User.first_name.ilike(f"%{first_name}%"))
    if email_domain:
        query = query.where(User.email.like(f"%{email_domain}%"))

    # Add ordering
    query = query.order_by(User.last_name, User.first_name)

    records = await db_ops.execute_one(query)
    logger.info(f"Retrieved {len(records)} filtered users")
    return {
        "records": records,
        "query_type": "Moderate SELECT with WHERE and ORDER BY",
        "filters_applied": {"first_name": first_name, "email_domain": email_domain, "query": str(query)}
    }


@app.get("/database/select-complex", tags=["Current - SELECT Operations"])
async def select_complex():
    """
    Complex SELECT: Join with aggregations, subqueries, and advanced filtering.

    Example:
        GET /database/select-complex

    Returns:
        Complex query results with user statistics.
    """
    logger.info("Complex SELECT with joins and aggregations")

    # Complex query with subquery and aggregation
    subquery = (
        select(func.count(Address.pkid).label('address_count'))
        .select_from(Address)
        .where(Address.user_id == User.pkid)
        .scalar_subquery()
    )

    query = (
        select(
            User.pkid,
            User.first_name,
            User.last_name,
            User.email,
            subquery.label('address_count'),
            func.length(User.first_name + User.last_name).label('name_length')
        )
        .where(
            and_(
                User.email.is_not(None),
                or_(
                    User.first_name.like('A%'),
                    User.last_name.like('S%')
                )
            )
        )
        .order_by(desc('address_count'), asc(User.last_name))
        .limit(20)
    )

    result = await db_ops.execute_one(query)
    logger.info("Complex SELECT query executed")

    return {
        "results": result,  # execute_one with SELECT returns list directly
        "query_type": "Complex SELECT with subquery, aggregation, and advanced WHERE",
        "result_count": len(result) if result else 0, "query": str(query)
    }


# INSERT Operations - Simple to Complex
@app.post("/database/insert-simple", status_code=201, tags=["Current - INSERT Operations"])
async def insert_simple(new_user: UserCreate):
    """
    Simple INSERT: Create a single user record.

    Example:
        POST /database/insert-simple
        {
            "first_name": "Alice",
            "last_name": "Smith",
            "email": "alice@example.com"
        }

    Returns:
        Insert operation result with metadata.
    """
    logger.info(f"Simple INSERT: {new_user}")

    query = insert(User).values(**new_user.dict())
    result = await db_ops.execute_one(query, return_metadata=True)

    logger.info(f"Insert result: {result}")
    return {
        "result": result,
        "query_type": "Simple INSERT",
        "user_data": new_user.dict(), "query": str(query)
    }


@app.post("/database/insert-moderate", status_code=201, tags=["Current - INSERT Operations"])
async def insert_moderate(users_data: list[UserCreate]):
    """
    Moderate INSERT: Create multiple user records in a single transaction.

    Example:
        POST /database/insert-moderate
        [
            {"first_name": "Alice", "last_name": "Smith", "email": "alice@example.com"},
            {"first_name": "Bob", "last_name": "Johnson", "email": "bob@example.com"}
        ]

    Returns:
        Batch insert results.
    """
    logger.info(f"Moderate INSERT: {len(users_data)} users")

    queries = [
        (insert(User), user.dict())
        for user in users_data
    ]

    result = await db_ops.execute_many(queries, return_results=True)
    logger.info(f"Batch insert completed: {len(result)} operations")

    return {
        "results": result,
        "query_type": "Moderate INSERT (batch)",
        "users_created": len(users_data), "query": str(queries)
    }


@app.post("/database/insert-complex", status_code=201, tags=["Current - INSERT Operations"])
async def insert_complex(count: int = Query(50, le=500, ge=1)):
    """
    Complex INSERT: Bulk insert with generated data and conditional logic.

    Example:
        POST /database/insert-complex?count=100

    Returns:
        Results of complex bulk insert with mixed data.
    """
    logger.info(f"Complex INSERT: generating {count} users")

    queries = []
    for i in range(count):
        # Generate varied data patterns
        token = secrets.token_hex(4)
        domain = "example.com" if i % 3 == 0 else f"domain{i%5}.org"

        # Some users get special prefixes
        if i % 10 == 0:
            first_name = f"Admin{token}"
        elif i % 7 == 0:
            first_name = f"Special{token}"
        else:
            first_name = f"User{token}{i}"

        queries.append((
            insert(User),
            {
                "first_name": first_name,
                "last_name": f"Generated{token}",
                "email": f"{first_name.lower()}{i}@{domain}"
            }
        ))

    # Execute with results tracking
    results = await db_ops.execute_many(queries, return_results=True)

    logger.info(f"Complex INSERT completed: {len(results)} users created")
    return {
        "total_created": len(results),
        "query_type": "Complex INSERT (bulk with generated data)",
        "sample_results": results[:3] if results else []  # Show first 3 results
        , "queries": str(queries)
    }


# UPDATE Operations - Simple to Complex
@app.put("/database/update-simple", tags=["Current - UPDATE Operations"])
async def update_simple(
    user_id: str = Query(..., description="User ID to update"),
    new_email: str = Query(..., description="New email address")
):
    """
    Simple UPDATE: Update a single user's email.

    Example:
        PUT /database/update-simple?user_id=some-uuid&new_email=newemail@example.com

    Returns:
        Update operation result.
    """
    logger.info(f"Simple UPDATE: user {user_id} email to {new_email}")

    query = (
        update(User)
        .where(User.pkid == user_id)
        .values(
            email=new_email,
            date_updated=datetime.datetime.now(datetime.timezone.utc)
        )
    )

    result = await db_ops.execute_one(query, return_metadata=True)
    logger.info(f"Update result: {result}")

    return {
        "result": result,
        "query_type": "Simple UPDATE",
        "updated_user_id": user_id, "query": str(query)
    }


@app.put("/database/update-moderate", tags=["Current - UPDATE Operations"])
async def update_moderate(email_domain: str = Query(..., description="Email domain to update")):
    """
    Moderate UPDATE: Update all users from a specific email domain.

    Example:
        PUT /database/update-moderate?email_domain=olddomain.com

    Returns:
        Batch update results.
    """
    logger.info(f"Moderate UPDATE: users with domain {email_domain}")

    # Update multiple records with conditional logic
    query = (
        update(User)
        .where(User.email.like(f"%@{email_domain}"))
        .values(
            email=func.replace(User.email, f"@{email_domain}", "@updated.com"),
            date_updated=datetime.datetime.now(datetime.timezone.utc)
        )
    )

    result = await db_ops.execute_one(query, return_metadata=True)
    logger.info(f"Moderate update result: {result}")

    return {
        "result": result,
        "query_type": "Moderate UPDATE (conditional batch)",
        "domain_updated": email_domain, "query": str(query)
    }


@app.put("/database/update-complex", tags=["Current - UPDATE Operations"])
async def update_complex():
    """
    Complex UPDATE: Multiple related updates in a transaction.

    Example:
        PUT /database/update-complex

    Returns:
        Results of complex multi-table updates.
    """
    logger.info("Complex UPDATE: multiple operations")

    queries = [
        # Update users with Admin prefix to have special email format
        (
            update(User)
            .where(User.first_name.like('Admin%'))
            .values(
                email=func.lower(User.first_name) + '@admin.company.com',
                date_updated=datetime.datetime.now(datetime.timezone.utc)
            ),
            None
        ),
        # Update users with long names
        (
            update(User)
            .where(func.length(User.first_name + User.last_name) > 20)
            .values(
                first_name=func.left(User.first_name, 10),
                last_name=func.left(User.last_name, 10),
                date_updated=datetime.datetime.now(datetime.timezone.utc)
            ),
            None
        )
    ]

    results = await db_ops.execute_many(queries, return_results=True)
    logger.info(f"Complex UPDATE completed: {len(results)} operations")

    return {
        "results": results,
        "query_type": "Complex UPDATE (multiple conditional updates)",
        "operations_completed": len(results), "queries": str(queries)
    }


# DELETE Operations - Simple to Complex
@app.delete("/database/delete-simple", tags=["Current - DELETE Operations"])
async def delete_simple(user_id: str = Query(..., description="User ID to delete")):
    """
    Simple DELETE: Delete a single user by ID.

    Example:
        DELETE /database/delete-simple?user_id=some-uuid

    Returns:
        Delete operation result.
    """
    logger.info(f"Simple DELETE: user {user_id}")

    query = delete(User).where(User.pkid == user_id)
    result = await db_ops.execute_one(query, return_metadata=True)

    logger.info(f"Delete result: {result}")
    return {
        "result": result,
        "query_type": "Simple DELETE",
        "deleted_user_id": user_id, "query": str(query)
    }


@app.delete("/database/delete-moderate", tags=["Current - DELETE Operations"])
async def delete_moderate(email_pattern: str = Query(..., description="Email pattern to match for deletion")):
    """
    Moderate DELETE: Delete users matching email pattern.

    Example:
        DELETE /database/delete-moderate?email_pattern=%test%

    Returns:
        Batch delete results.
    """
    logger.info(f"Moderate DELETE: users matching email pattern {email_pattern}")

    query = delete(User).where(User.email.like(email_pattern))
    result = await db_ops.execute_one(query, return_metadata=True)

    logger.info(f"Moderate delete result: {result}")
    return {
        "result": result,
        "query_type": "Moderate DELETE (pattern-based)",
        "email_pattern": email_pattern, "query": str(query)
    }


@app.delete("/database/delete-complex", tags=["Current - DELETE Operations"])
async def delete_complex():
    """
    Complex DELETE: Conditional cascading delete with multiple criteria.

    Example:
        DELETE /database/delete-complex

    Returns:
        Results of complex delete operations.
    """
    logger.info("Complex DELETE: multiple criteria")

    queries = [
        # Delete users with specific name patterns and no addresses
        (
            delete(User)
            .where(
                and_(
                    User.first_name.like('Generated%'),
                    ~User.addresses.any()  # Users with no addresses
                )
            ),
            None
        ),
        # Delete users with old email domains
        (
            delete(User)
            .where(
                or_(
                    User.email.like('%@olddomain.com'),
                    User.email.like('%@deprecated.org')
                )
            ),
            None
        )
    ]

    results = await db_ops.execute_many(queries, return_results=True)
    logger.info(f"Complex DELETE completed: {len(results)} operations")

    return {
        "results": results,
        "query_type": "Complex DELETE (multiple criteria and conditions)",
        "operations_completed": len(results),
        "queries": str(queries)
    }


# Advanced Operations
@app.get("/database/read-multi-query", tags=["Current - Advanced Operations"])
async def read_multi_query():
    """
    Execute multiple SELECT queries simultaneously.

    Example:
        GET /database/read-multi-query

    Returns:
        Results from multiple queries.
    """
    logger.info("Executing multiple queries")

    queries = {
        "total_users": select(func.count(User.pkid)),
        "recent_users": select(User).where(User.date_created >= datetime.date.today()).limit(5),
        "email_domains": select(
            func.substr(User.email, func.instr(User.email, '@') + 1).label('domain'),
            func.count().label('count')
        ).where(User.email.is_not(None)).group_by('domain'),
        "user_stats": select(
            func.min(func.length(User.first_name)).label('min_name_length'),
            func.max(func.length(User.first_name)).label('max_name_length'),
            func.avg(func.length(User.first_name)).label('avg_name_length')
        )
    }

    results = await db_ops.read_multi_query(queries)
    logger.info("Multi-query completed")

    return {
        "results": results,
        "query_type": "Multiple SELECT queries",
        "queries_executed": list(queries.keys()),
        "queries": str(queries)
    }


@app.get("/database/get-one-record", tags=["Current - Advanced Operations"])
async def read_one_record(record_id: str):
    """
    Retrieve a single User record by primary key using read_one_record.

    Example:
        GET /database/get-one-record?record_id=some-uuid

    Returns:
        The User record with the given primary key.
    """
    logger.info(f"Reading one record with id {record_id}")
    record = await db_ops.read_one_record(select(User).where(User.pkid == record_id))
    logger.info(f"Record with id {record_id}: {record}")
    return {"record": record, "query": str(select(User).where(User.pkid == record_id))}


# ===================================================================
# DEPRECATED DATABASE OPERATIONS (Legacy Methods)
# These methods are deprecated and should not be used in new code
# ===================================================================

@app.post("/database/deprecated-create-one", status_code=201, tags=["Deprecated - Legacy Operations"])
async def deprecated_create_one(new_user: UserCreate):
    """
    [DEPRECATED] Create a single user using the deprecated create_one method.

    ⚠️  This method is deprecated. Use /database/insert-simple instead.

    Example:
        POST /database/deprecated-create-one
        {
            "first_name": "Alice",
            "last_name": "Smith",
            "email": "alice@example.com"
        }

    Returns:
        The created User record.
    """
    logger.warning("Using deprecated create_one method")
    user = User(**new_user.dict())
    record = await db_ops.create_one(user)
    logger.info(f"Created record using deprecated method: {record}")
    return {
        "record": record,
        "warning": "This method is deprecated. Use execute_one with INSERT instead.",
        "recommended_endpoint": "/database/insert-simple"
    }


@app.post("/database/deprecated-create-many", status_code=201, tags=["Deprecated - Legacy Operations"])
async def deprecated_create_many(count: int = Query(5, le=50, ge=1)):
    """
    [DEPRECATED] Create multiple users using the deprecated create_many method.

    ⚠️  This method is deprecated. Use /database/insert-moderate or /database/insert-complex instead.

    Example:
        POST /database/deprecated-create-many?count=10

    Returns:
        The created User records.
    """
    logger.warning(f"Using deprecated create_many method for {count} users")

    users = []
    for i in range(count):
        token = secrets.token_hex(4)
        user = User(
            first_name=f"DepUser{token}{i}",
            last_name=f"Legacy{token}",
            email=f"deprecated{token}{i}@example.com"
        )
        users.append(user)

    records = await db_ops.create_many(users)
    logger.info(f"Created {len(records)} records using deprecated method")

    return {
        "records": records,
        "count": len(records),
        "warning": "This method is deprecated. Use execute_many with INSERT instead.",
        "recommended_endpoints": ["/database/insert-moderate", "/database/insert-complex"]
    }


@app.put("/database/deprecated-update-one", tags=["Deprecated - Legacy Operations"])
async def deprecated_update_one(
    user_id: str = Query(..., description="User ID to update"),
    first_name: str = Query(None, description="New first name"),
    last_name: str = Query(None, description="New last name"),
    email: str = Query(None, description="New email")
):
    """
    [DEPRECATED] Update a user using the deprecated update_one method.

    ⚠️  This method is deprecated. Use /database/update-simple, /database/update-moderate, or /database/update-complex instead.

    Example:
        PUT /database/deprecated-update-one?user_id=some-uuid&email=newemail@example.com

    Returns:
        The update result.
    """
    logger.warning(f"Using deprecated update_one method for user {user_id}")

    new_values = {}
    if first_name:
        new_values["first_name"] = first_name
    if last_name:
        new_values["last_name"] = last_name
    if email:
        new_values["email"] = email

    if new_values:
        new_values["date_updated"] = datetime.datetime.now(datetime.timezone.utc)

    result = await db_ops.update_one(table=User, record_id=user_id, new_values=new_values)
    logger.info(f"Updated user {user_id} using deprecated method")

    return {
        "result": result,
        "updated_fields": new_values,
        "warning": "This method is deprecated. Use execute_one with UPDATE instead.",
        "recommended_endpoints": ["/database/update-simple", "/database/update-moderate", "/database/update-complex"]
    }


@app.delete("/database/deprecated-delete-one", tags=["Deprecated - Legacy Operations"])
async def deprecated_delete_one(user_id: str = Query(..., description="User ID to delete")):
    """
    [DEPRECATED] Delete a user using the deprecated delete_one method.

    ⚠️  This method is deprecated. Use /database/delete-simple instead.

    Example:
        DELETE /database/deprecated-delete-one?user_id=some-uuid

    Returns:
        The delete result.
    """
    logger.warning(f"Using deprecated delete_one method for user {user_id}")

    result = await db_ops.delete_one(table=User, record_id=user_id)
    logger.info(f"Deleted user {user_id} using deprecated method")

    return {
        "result": result,
        "deleted_user_id": user_id,
        "warning": "This method is deprecated. Use execute_one with DELETE instead.",
        "recommended_endpoint": "/database/delete-simple"
    }


@app.delete("/database/deprecated-delete-many", tags=["Deprecated - Legacy Operations"])
async def deprecated_delete_many(user_ids: list[str] = Body(..., description="List of User IDs to delete")):
    """
    [DEPRECATED] Delete multiple users using the deprecated delete_many method.

    ⚠️  This method is deprecated. Use /database/delete-moderate or /database/delete-complex instead.

    Example:
        DELETE /database/deprecated-delete-many
        ["user-id-1", "user-id-2", "user-id-3"]

    Returns:
        The delete results.
    """
    logger.warning(f"Using deprecated delete_many method for {len(user_ids)} users")

    result = await db_ops.delete_many(table=User, id_column_name="pkid", id_values=user_ids)
    logger.info(f"Deleted {len(user_ids)} users using deprecated method")

    return {
        "result": result,
        "deleted_count": len(user_ids),
        "warning": "This method is deprecated. Use execute_one/execute_many with DELETE instead.",
        "recommended_endpoints": ["/database/delete-moderate", "/database/delete-complex"]
    }


# ===================================================================
# UTILITY AND EXAMPLE ENDPOINTS
# Additional examples and utility functions
# ===================================================================

@app.get("/database/example-error-handling", tags=["Utility - Examples"])
async def example_error_handling():
    """
    Demonstrate error handling with invalid queries.

    Example:
        GET /database/example-error-handling

    Returns:
        Error handling examples.
    """
    logger.info("Demonstrating error handling")

    # Try an invalid query to show error handling
    try:
        result = await db_ops.execute_one(text("SELECT * FROM non_existent_table"))
        return {"result": result}
    except Exception as e:
        return {
            "error_demonstration": True,
            "error_details": str(e),
            "message": "This demonstrates how the database operations handle errors gracefully"
        }


@app.get("/database/raw-sql-example", tags=["Utility - Examples"])
async def raw_sql_example():
    """
    Example of using raw SQL with execute_one.

    Example:
        GET /database/raw-sql-example

    Returns:
        Results from raw SQL query.
    """
    logger.info("Executing raw SQL example")

    # Raw SQL query using text()
    raw_query = text("""
        SELECT
            first_name,
            last_name,
            CASE
                WHEN email LIKE '%@example.com' THEN 'Example Domain'
                WHEN email LIKE '%@admin.%' THEN 'Admin Domain'
                ELSE 'Other Domain'
            END as domain_category,
            LENGTH(first_name || last_name) as full_name_length
        FROM users
        WHERE email IS NOT NULL
        ORDER BY full_name_length DESC
        LIMIT 10
    """)

    result = await db_ops.execute_one(raw_query, return_metadata=True)

    return {
        "results": result.get("rows", []),
        "query_type": "Raw SQL with CASE statements and string functions",
        "rowcount": result.get("rowcount")
    }


@app.get("/database/performance-comparison", tags=["Utility - Examples"])
async def performance_comparison():
    """
    Compare performance between different query approaches.

    Example:
        GET /database/performance-comparison

    Returns:
        Performance timing comparisons.
    """
    logger.info("Running performance comparison")

    # Time different approaches

    # Approach 1: Single execute_one with complex query
    start_time = time.time()
    complex_query = (
        select(User.pkid, User.first_name, User.email)
        .where(User.email.is_not(None))
        .order_by(User.first_name)
        .limit(100)
    )
    result1 = await db_ops.execute_one(complex_query)
    time1 = time.time() - start_time

    # Approach 2: Multiple simple queries
    start_time = time.time()
    queries = {
        "basic_users": select(User).limit(50),
        "email_count": select(func.count(User.pkid)).where(User.email.is_not(None)),
        "name_stats": select(
            func.min(func.length(User.first_name)).label('min_len'),
            func.max(func.length(User.first_name)).label('max_len')
        )
    }
    await db_ops.read_multi_query(queries)
    time2 = time.time() - start_time

    return {
        "approach_1": {
            "description": "Single complex query with execute_one",
            "time_seconds": round(time1, 4),
            "result_count": len(result1) if isinstance(result1, list) else 1
        },
        "approach_2": {
            "description": "Multiple queries with read_multi_query",
            "time_seconds": round(time2, 4),
            "queries_executed": len(queries)
        },
        "performance_note": "Results may vary based on data size and system performance"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=5001)
