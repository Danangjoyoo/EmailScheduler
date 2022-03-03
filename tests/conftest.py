import pytest, os, dotenv
from httpx import AsyncClient, Client
from typing import Generator, AsyncIterator
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from app.database.connection import Base
from main import app as my_app, generate_database_session, g
import asyncio

# database_url = "sqlite:///./database/test.db"
# async_database_url = "sqlite+aiosqlite:///./database/test.db"

# @event.listens_for(Engine, "connect")
# def _set_sqlite_pragma(dbapi_connection, connection_record):
#     cursor = dbapi_connection.cursor()
#     cursor.execute("PRAGMA foreign_keys=ON;")
#     cursor.close()

# test_async_engine = create_async_engine(async_database_url, echo=False, future=True)
# test_async_session = sessionmaker(bind=test_async_engine, autocommit=False, class_=AsyncSession, expire_on_commit=False)

# async def generate_test_database_session():    
#     async with test_async_session() as sess:
#         g.session = sess

# async def startup_test():
#     async with test_async_engine.begin() as e:
#         await e.run_sync(Base.metadata.drop_all)
#         await e.run_sync(Base.metadata.create_all)

database_url = "sqlite:///./database/app.db"

sync_engine = create_engine(database_url, echo=True, future=True)
sync_session = sessionmaker(bind=sync_engine, autocommit=False, expire_on_commit=False)

@pytest.fixture
def app():
    my_app.config.update({
        "TESTING": True
    })
    
    # # override startup function
    # my_app.before_first_request_funcs[0] = startup_test

    # # override the default session generator (bind to new db url)
    # my_app.before_request_funcs[None][0] = generate_test_database_session

    Base.metadata.create_all(sync_engine)
    
    yield my_app

    Base.metadata.drop_all(sync_engine)

@pytest.fixture
def client(app):
    return my_app.test_client()