# -*- coding: utf-8 -*-
import datetime
from uuid import uuid4

import pytest
from sqlalchemy import Column, String
from sqlalchemy.orm import Session, declarative_base

from devsetgo_toolkit import SchemaBase

Base = declarative_base()


class User(SchemaBase, Base):
    __tablename__ = "test_table"
    name_first = Column(String, unique=False, index=True)


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set up a SQLite database in memory
engine = create_engine("sqlite:///:memory:")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)  # Create the schema


@pytest.fixture
def db_session():
    # Create a new database session for a test
    session = SessionLocal()

    try:
        yield session  # this is where the testing happens!
    finally:
        session.close()  # we make sure to close the session after the test has been run


def test_schema_base(db_session: Session):
    user = User()
    user.name_first = "Test"

    # Add the instance to the session and commit it to generate id
    db_session.add(user)
    db_session.commit()

    # Assert id is a valid UUID
    assert isinstance(user.id, str)

    # Assert date_created and date_updated are set upon creation
    assert isinstance(user.date_created, datetime.datetime)
    assert isinstance(user.date_updated, datetime.datetime)

    # Update the instance and commit changes
    user.id = str(uuid4())
    db_session.commit()

    # Assert date_updated is updated after editing
    assert isinstance(user.date_updated, datetime.datetime)
