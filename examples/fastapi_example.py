# -*- coding: utf-8 -*-
"""
Author: Mike Ryan
Date: 2024/05/16
License: MIT
"""
import datetime
import secrets
import time
from contextlib import asynccontextmanager

from fastapi import Body, FastAPI, Query
from fastapi.responses import RedirectResponse
from loguru import logger
from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, ForeignKey, Select, String
from sqlalchemy.orm import relationship
from tqdm import tqdm
from dsg_lib.fastapi_functions import system_health_endpoints  # , system_tools_endpoints

from dsg_lib.async_database_functions import (
    async_database,
    base_schema,
    database_config,
    database_operations,
)
from dsg_lib.common_functions import logging_config

logging_config.config_log(logging_level='INFO', log_serializer=False, log_name='log.log')


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info('starting up')
    # Create the tables in the database
    await async_db.create_tables()

    create_users = True
    if create_users:
        await create_a_bunch_of_users(single_entry=24, many_entries=2000)
    yield
    logger.info('shutting down')


# Create an instance of the FastAPI class
app = FastAPI(
    title='FastAPI Example',  # The title of the API
    description='This is an example of a FastAPI application using the DevSetGo Toolkit.',  # A brief description of the API
    version='0.1.0',  # The version of the API
    docs_url='/docs',  # The URL where the API documentation will be served
    redoc_url='/redoc',  # The URL where the ReDoc documentation will be served
    openapi_url='/openapi.json',  # The URL where the OpenAPI schema will be served
    debug=True,  # Enable debug mode
    middleware=[],  # A list of middleware to include in the application
    routes=[],  # A list of routes to include in the application
    lifespan=lifespan,  # this is the replacement for the startup and shutdown events
)


@app.get('/')
async def root():
    """
    Root endpoint of API
    Returns:
        Redrects to openapi document
    """
    # redirect to openapi docs
    logger.info('Redirecting to OpenAPI docs')
    response = RedirectResponse(url='/docs')
    return response



config_health = {
    'enable_status_endpoint': True,
    'enable_uptime_endpoint': True,
    'enable_heapdump_endpoint': True,
}
app.include_router(
    system_health_endpoints.create_health_router(config=config_health),
    prefix='/api/health',
    tags=['system-health'],
)

# Create a DBConfig instance
config = {
    # "database_uri": "postgresql+asyncpg://postgres:postgres@postgresdb/postgres",
    'database_uri': 'sqlite+aiosqlite:///:memory:?cache=shared',
    'echo': False,
    'future': True,
    # "pool_pre_ping": True,
    # "pool_size": 10,
    # "max_overflow": 10,
    'pool_recycle': 3600,
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

    __tablename__ = 'users'
    __table_args__ = {
        'comment': 'User table storing user details like first name, last name, and email'
    }

    first_name = Column(String(50), unique=False, index=True)  # First name of the user
    last_name = Column(String(50), unique=False, index=True)  # Last name of the user
    email = Column(
        String(200), unique=True, index=True, nullable=True
    )  # Email of the user, must be unique
    addresses = relationship(
        'Address', order_by='Address.pkid', back_populates='user'
    )  # Relationship to the Address class


class Address(base_schema.SchemaBaseSQLite, async_db.Base):
    """
    Address table storing address details like street, city, and zip code
    """

    __tablename__ = 'addresses'
    __table_args__ = {
        'comment': 'Address table storing address details like street, city, and zip code'
    }

    street = Column(String(200), unique=False, index=True)  # Street of the address
    city = Column(String(200), unique=False, index=True)  # City of the address
    zip = Column(String(50), unique=False, index=True)  # Zip code of the address
    user_id = Column(String(36), ForeignKey('users.pkid'))  # Foreign key to the User table
    user = relationship('User', back_populates='addresses')  # Relationship to the User class


async def create_a_bunch_of_users(single_entry=0, many_entries=0):
    logger.info(f'single_entry: {single_entry}')
    await async_db.create_tables()
    # Create a list to hold the user data

    # Create a loop to generate user data

    for _ in tqdm(range(single_entry), desc='executing one'):
        value = secrets.token_hex(16)
        user = User(
            first_name=f'First{value}',
            last_name=f'Last{value}',
            email=f'user{value}@example.com',
        )
        logger.info(f'created_users: {user}')
        await db_ops.create_one(user)

    users = []
    # Create a loop to generate user data
    for i in tqdm(range(many_entries), desc='executing many'):
        value_one = secrets.token_hex(4)
        value_two = secrets.token_hex(8)
        user = User(
            first_name=f'First{value_one}{i}{value_two}',
            last_name=f'Last{value_one}{i}{value_two}',
            email=f'user{value_one}{i}{value_two}@example.com',
        )
        logger.info(f'created_users: {user.first_name}')
        users.append(user)

    # Use db_ops to add the users to the database
    await db_ops.create_many(users)


@app.get('/database/get-primary-key', tags=['Database Examples'])
async def table_primary_key():
    logger.info('Getting primary key of User table')
    pk = await db_ops.get_primary_keys(User)
    logger.info(f'Primary key of User table: {pk}')
    return {'pk': pk}


@app.get('/database/get-column-details', tags=['Database Examples'])
async def table_column_details():
    logger.info('Getting column details of User table')
    columns = await db_ops.get_columns_details(User)
    logger.info(f'Column details of User table: {columns}')
    return {'columns': columns}


@app.get('/database/get-tables', tags=['Database Examples'])
async def table_table_details():
    logger.info('Getting table names')
    tables = await db_ops.get_table_names()
    logger.info(f'Table names: {tables}')
    return {'table_names': tables}


@app.get('/database/get-count', tags=['Database Examples'])
async def get_count():
    logger.info('Getting count of users')
    count = await db_ops.count_query(Select(User))
    logger.info(f'Count of users: {count}')
    return {'count': count}


@app.get('/database/get-all', tags=['Database Examples'])
async def get_all(offset: int = 0, limit: int = Query(100, le=100000, ge=1)):
    logger.info(f'Getting all users with offset {offset} and limit {limit}')
    records = await db_ops.read_query(Select(User).offset(offset).limit(limit))
    logger.info(f'Retrieved {len(records)} users')
    return {'records': records}


@app.get('/database/get-one-record', tags=['Database Examples'])
async def read_one_record(record_id: str):
    logger.info(f'Reading one record with id {record_id}')
    record = await db_ops.read_one_record(Select(User).where(User.pkid == record_id))
    logger.info(f'Record with id {record_id}: {record}')
    return record


class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr


class UserCreate(UserBase):
    pass


@app.post('/database/create-one-record', status_code=201, tags=['Database Examples'])
async def create_one_record(new_user: UserCreate):
    logger.info(f'Creating one record: {new_user}')
    user = User(**new_user.dict())
    record = await db_ops.create_one(user)
    logger.info(f'Created record: {record}')
    return record


@app.post('/database/create-many-records', status_code=201, tags=['Database Examples'])
async def create_many_records(number_of_users: int = Query(100, le=1000, ge=1)):
    logger.info(f'Creating {number_of_users} records')
    t0 = time.time()
    users = []
    # Create a loop to generate user data
    for i in tqdm(range(number_of_users), desc='executing many'):
        value_one = secrets.token_hex(4)
        value_two = secrets.token_hex(8)
        user = User(
            first_name=f'First{value_one}{i}{value_two}',
            last_name=f'Last{value_one}{i}{value_two}',
            email=f'user{value_one}{i}{value_two}@example.com',
        )
        logger.info(f'Created user: {user.first_name}')
        users.append(user)

    # Use db_ops to add the users to the database
    await db_ops.create_many(users)
    t1 = time.time()
    process_time = format(t1 - t0, '.4f')
    logger.info(f'Created {number_of_users} records in {process_time} seconds')
    return {'number_of_users': number_of_users, 'process_time': process_time}


@app.put('/database/update-one-record', status_code=200, tags=['Database Examples'])
async def update_one_record(
    id: str = Body(
        ...,
        description='UUID to update',
        examples=['6087cce8-0bdd-48c2-ba96-7d557dae843e'],
    ),
    first_name: str = Body(..., examples=['Agent']),
    last_name: str = Body(..., examples=['Smith']),
    email: str = Body(..., examples=['jim@something.com']),
):
    logger.info(f'Updating one record with id {id}')
    # adding date_updated to new_values as it is not supported in sqlite \
    # and other database may not either.
    new_values = {
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'date_updated': datetime.datetime.now(datetime.timezone.utc),
    }
    record = await db_ops.update_one(table=User, record_id=id, new_values=new_values)
    logger.info(f'Updated record with id {id}')
    return record


@app.delete('/database/delete-one-record', status_code=200, tags=['Database Examples'])
async def delete_one_record(record_id: str = Body(...)):
    logger.info(f'Deleting one record with id {record_id}')
    record = await db_ops.delete_one(table=User, record_id=record_id)
    logger.info(f'Deleted record with id {record_id}')
    return record


@app.delete(
    '/database/delete-many-records-aka-this-is-a-bad-idea',
    status_code=201,
    tags=['Database Examples'],
)
async def delete_many_records(id_values: list = Body(...), id_column_name: str = 'pkid'):
    logger.info(f'Deleting many records with ids {id_values}')
    record = await db_ops.delete_many(table=User, id_column_name='pkid', id_values=id_values)
    logger.info(f'Deleted records with ids {id_values}')
    return record


@app.get(
    '/database/get-list-of-records-to-paste-into-delete-many-records',
    tags=['Database Examples'],
)
async def read_list_of_records(
    offset: int = Query(0, le=1000, ge=0), limit: int = Query(100, le=10000, ge=1)
):
    logger.info(f'Reading list of records with offset {offset} and limit {limit}')
    records = await db_ops.read_query(Select(User), offset=offset, limit=limit)
    records_list = []
    for record in records:
        records_list.append(record.pkid)
    logger.info(f'Read list of records: {records_list}')
    return records_list


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='127.0.0.1', port=5000)
