import os
from sqlalchemy import event, ForeignKeyConstraint
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine
from sqlite3 import Connection as SQLite3Connection

from .models import Base

database_url = os.getenv("DATABASE_URL")

if "sqlite" in database_url:
    try:
        os.remove("./database/app.db")
    except:
        pass

    @event.listens_for(Engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()

engine = create_async_engine(database_url, echo=False, future=True)    

session = sessionmaker(bind=engine, autocommit=False, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    async with engine.begin() as e:
        await e.run_sync(Base.metadata.drop_all)
        await e.run_sync(Base.metadata.create_all)