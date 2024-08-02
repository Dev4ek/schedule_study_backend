from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import create_engine
import os
from sqlalchemy.orm import sessionmaker
from . import base_ORM
from loguru import logger
from sqlalchemy_utils import database_exists, create_database


async def get_engine(sync=False):

    if not sync:
        engine = create_async_engine(

                                    url=os.getenv('database_url'),
                                    echo=False,
                                )
    else:
        engine = create_engine(
                                    url=os.getenv('sync_database_url'),
                                    echo=False,
                                )
    return engine
    


async def get_session():
    engine = await get_engine()

    sessionmaker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with sessionmaker() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_tables():
    engine = await get_engine(sync=True)

    if not database_exists(engine.url):
        create_database(engine.url)
        logger.success("database created successfully")

    logger.debug("creating tables...")

    base_ORM.Base.metadata.create_all(engine, checkfirst=True)
    logger.info("tables created successfully")
    return True


# async def drop_tables():
#     engine = await get_engine(async_eng=True)
#     async with engine.begin() as conn:
#         await conn.run_sync(base.Base.metadata.drop_all)
# async def create_database():

#     engine = create_engine(os.getenv("postgres_url"))

#     with engine.connect() as conn:
#         conn.execute(f"CREATE DATABASE schedule")
#         logger.info("database created successfully")
