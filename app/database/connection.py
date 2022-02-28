import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from .models import Base

database_url = os.getenv("DATABASE_URL")

engine = create_async_engine(database_url)

session = sessionmaker(bind=engine, autocommit=False, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    async with engine.begin() as e:
        await e.run_sync(Base.metadata.drop_all)
        await e.run_sync(Base.metadata.create_all)