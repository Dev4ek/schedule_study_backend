from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import create_engine
import os
from sqlalchemy.orm import sessionmaker
from . import base_ORM
from loguru import logger


async def get_engine(sync=False):

    if not sync:
        engine = create_async_engine(

                                    url=os.getenv('database_url'),
                                    echo=True,
                                )
    else:
        engine = create_engine(
                                    url=os.getenv('sync_database_url'),
                                    echo=True,
                                )
    return engine
    



async def get_session():
    engine = await get_engine()

    Session_ = sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
        )
    
    return Session_()


async def create_tables():
    logger.debug("creating tables...")
    engine = await get_engine(sync=True)

    base_ORM.Base.metadata.create_all(engine, checkfirst=True)
    logger.info("tables created successfully")
    return True


# async def drop_tables():
#     engine = await get_engine(async_eng=True)
#     async with engine.begin() as conn:
#         await conn.run_sync(base.Base.metadata.drop_all)