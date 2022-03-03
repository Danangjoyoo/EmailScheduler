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

database_url = "sqlite:///./database/app.db"

sync_engine = create_engine(database_url, echo=True, future=True)
sync_session = sessionmaker(bind=sync_engine, autocommit=False, expire_on_commit=False)

@pytest.fixture
def app():
    my_app.config.update({
        "TESTING": True
    })
    Base.metadata.create_all(sync_engine)    
    yield my_app
    Base.metadata.drop_all(sync_engine)

@pytest.fixture
def client(app):
    return my_app.test_client()