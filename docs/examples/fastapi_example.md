# FastAPI Example Module

This module demonstrates the use of FastAPI in conjunction with the DevSetGo Toolkit to create a comprehensive API showcasing modern database operations. It includes examples of current/recommended database operations, deprecated methods for comparison, and system health endpoints. The module is designed to showcase best practices for building scalable and maintainable FastAPI applications with proper database operation patterns.

[Full FastAPI Code Example](https://github.com/devsetgo/devsetgo_lib/blob/main/examples/fastapi_example.py)


## Features

- **Modern Database Integration**:
  - Uses SQLAlchemy for ORM and database interactions with the new `execute_one` and `execute_many` methods
  - Supports SQLite (in-memory) for demonstration purposes
  - Includes models for `User` and `Address` tables with relationships
  - Demonstrates both current and deprecated database operation patterns

- **Comprehensive API Endpoints**:
  - **Current/Recommended Operations**: Using `execute_one`, `execute_many`, `read_query`, etc.
  - **Deprecated Operations**: Legacy methods for comparison and migration guidance
  - **Utility Examples**: Error handling, raw SQL, and performance comparisons
  - System health endpoints for monitoring uptime, heap dumps, and status
  - Robots.txt endpoint for bot management

- **Database Operation Examples**:
  - **Simple**: Basic single-table operations
  - **Moderate**: Multi-condition filtering and batch operations
  - **Complex**: Advanced queries with joins, subqueries, and aggregations

- **Logging**:
  - Configured using `loguru` for structured and detailed logging
  - Logs API requests, database operations, and system events

- **Asynchronous Operations**:
  - Fully asynchronous database operations using `aiosqlite`
  - Asynchronous lifespan management for startup and shutdown events

- **Configuration**:
  - Modular configuration for database, logging, and API behavior
  - Bot management configuration for controlling access to the API

## Usage

### Running the Application

1. **Using Make Command** (Recommended):
   ```bash
   make ex-fastapi
   ```

2. **Direct Command**:
   ```bash
   uvicorn examples.fastapi_example:app --host 127.0.0.1 --port 5001
   ```

### Accessing the API

- **OpenAPI Documentation**: [http://127.0.0.1:5001/docs](http://127.0.0.1:5001/docs)
- **ReDoc Documentation**: [http://127.0.0.1:5001/redoc](http://127.0.0.1:5001/redoc)

## API Endpoint Categories

### Current/Recommended Operations

These endpoints demonstrate the modern approach using the new database operation methods:

#### Database Metadata
- `GET /database/get-primary-key` - Get table primary keys
- `GET /database/get-column-details` - Get column metadata
- `GET /database/get-tables` - List all tables
- `GET /database/get-count` - Count records using `count_query`

#### SELECT Operations
- `GET /database/select-simple` - Basic SELECT with pagination
- `GET /database/select-moderate` - Filtered SELECT with ordering
- `GET /database/select-complex` - Advanced SELECT with joins and subqueries

#### INSERT Operations
- `POST /database/insert-simple` - Single record insert using `execute_one`
- `POST /database/insert-moderate` - Batch insert using `execute_many`
- `POST /database/insert-complex` - Bulk insert with generated data

#### UPDATE Operations
- `PUT /database/update-simple` - Single record update
- `PUT /database/update-moderate` - Conditional batch updates
- `PUT /database/update-complex` - Multiple related updates in transaction

#### DELETE Operations
- `DELETE /database/delete-simple` - Single record deletion
- `DELETE /database/delete-moderate` - Pattern-based deletion
- `DELETE /database/delete-complex` - Complex conditional deletions

#### Advanced Operations
- `GET /database/read-multi-query` - Execute multiple queries simultaneously
- `GET /database/get-one-record` - Single record retrieval using `read_one_record`

### Deprecated Operations (Legacy)

⚠️ **These endpoints demonstrate deprecated methods and should not be used in new code:**

- `POST /database/deprecated-create-one` - Legacy `create_one` method
- `POST /database/deprecated-create-many` - Legacy `create_many` method
- `PUT /database/deprecated-update-one` - Legacy `update_one` method
- `DELETE /database/deprecated-delete-one` - Legacy `delete_one` method
- `DELETE /database/deprecated-delete-many` - Legacy `delete_many` method

Each deprecated endpoint includes:
- ⚠️ Warning messages about deprecation
- Recommended alternative endpoints
- Migration guidance

### Utility and Examples

- `GET /database/example-error-handling` - Error handling demonstration
- `GET /database/raw-sql-example` - Raw SQL queries with `text()`
- `GET /database/performance-comparison` - Performance comparisons between approaches

## Code Examples

### Basic Setup

```python
import datetime
import secrets
import time
from contextlib import asynccontextmanager

from fastapi import Body, FastAPI, Query
from fastapi.responses import RedirectResponse
from loguru import logger
from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, ForeignKey, String, and_, delete, insert, or_, update, select, text, func, desc, asc
from sqlalchemy.orm import relationship
from tqdm import tqdm

from dsg_lib.async_database_functions import (
    async_database,
    base_schema,
    database_config,
    database_operations,
)
```

### Database Configuration

```python
# Create database configuration
config = {
    "database_uri": "sqlite+aiosqlite:///:memory:?cache=shared",
    "echo": False,
    "future": True,
    "pool_recycle": 3600,
}

db_config = database_config.DBConfig(config)
async_db = async_database.AsyncDatabase(db_config)
db_ops = database_operations.DatabaseOperations(async_db)
```

### Model Definitions

```python
class User(base_schema.SchemaBaseSQLite, async_db.Base):
    """User table storing user details like first name, last name, and email"""

    __tablename__ = "users"
    __table_args__ = {
        "comment": "User table storing user details like first name, last name, and email"
    }

    first_name = Column(String(50), unique=False, index=True)
    last_name = Column(String(50), unique=False, index=True)
    email = Column(String(200), unique=True, index=True, nullable=True)
    addresses = relationship("Address", order_by="Address.pkid", back_populates="user")
```

### Current Database Operations Examples

#### Simple INSERT
```python
@app.post("/database/insert-simple", status_code=201, tags=["Current - INSERT Operations"])
async def insert_simple(new_user: UserCreate):
    query = insert(User).values(**new_user.dict())
    result = await db_ops.execute_one(query, return_metadata=True)
    return {"result": result, "query_type": "Simple INSERT"}
```

#### Complex SELECT with Subqueries
```python
@app.get("/database/select-complex", tags=["Current - SELECT Operations"])
async def select_complex():
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
    return {"results": result, "query_type": "Complex SELECT"}
```

#### Batch Operations with execute_many
```python
@app.post("/database/insert-moderate", status_code=201, tags=["Current - INSERT Operations"])
async def insert_moderate(users_data: list[UserCreate]):
    queries = [
        (insert(User), user.dict())
        for user in users_data
    ]

    result = await db_ops.execute_many(queries, return_results=True)
    return {"results": result, "users_created": len(users_data)}
```

### Migration from Deprecated Methods

#### Old Way (Deprecated)
```python
# ❌ Don't use - Deprecated
user = User(first_name="John", last_name="Doe", email="john@example.com")
result = await db_ops.create_one(user)
```

#### New Way (Recommended)
```python
# ✅ Use this instead
query = insert(User).values(first_name="John", last_name="Doe", email="john@example.com")
result = await db_ops.execute_one(query, return_metadata=True)
```

## Key Differences: Current vs Deprecated

| Operation | Deprecated Method | Current Method | Benefits |
|-----------|------------------|----------------|----------|
| Single Insert | `create_one(record)` | `execute_one(insert().values())` | More explicit, better error handling, metadata support |
| Batch Insert | `create_many(records)` | `execute_many([(insert(), values)])` | Transaction control, mixed operations support |
| Update | `update_one(table, id, values)` | `execute_one(update().where().values())` | More flexible conditions, better SQL control |
| Delete | `delete_one(table, id)` | `execute_one(delete().where())` | More flexible conditions, better SQL control |
| Select | `read_query(query)` | `execute_one(select())` for simple, `read_query()` for complex | Unified interface, consistent returns |

## Error Handling

The API includes comprehensive error handling examples:

```python
@app.get("/database/example-error-handling")
async def example_error_handling():
    try:
        result = await db_ops.execute_one(text("SELECT * FROM non_existent_table"))
        return {"result": result}
    except Exception as e:
        return {
            "error_demonstration": True,
            "error_details": str(e),
            "message": "This demonstrates graceful error handling"
        }
```

## Performance Examples

The API includes performance comparison endpoints that demonstrate:
- Single complex query vs multiple simple queries
- Different query optimization techniques
- Timing comparisons for various approaches

## Health Monitoring

System health endpoints are included:
- `/api/health/status` - Application status
- `/api/health/uptime` - Application uptime
- `/api/health/heapdump` - Memory usage information

## Dependencies

- **FastAPI**: Web framework for building APIs
- **SQLAlchemy**: ORM for database interactions
- **loguru**: Logging library for structured logs
- **tqdm**: Progress bar for bulk operations
- **pydantic**: Data validation and settings management
- **DevSetGo Toolkit**: Custom library for database and common utility functions

## Best Practices Demonstrated

1. **Use Current Methods**: Always use `execute_one`/`execute_many` for new code
2. **Explicit Queries**: Write explicit SQLAlchemy queries instead of ORM shortcuts
3. **Transaction Management**: Use `execute_many` for related operations
4. **Error Handling**: Implement comprehensive error handling with meaningful messages
5. **Metadata Usage**: Use `return_metadata=True` for DML operations when you need details
6. **Query Organization**: Organize endpoints by operation complexity (simple → moderate → complex)
7. **Documentation**: Include clear examples and migration paths from deprecated methods

## License
This module is licensed under the MIT License.
