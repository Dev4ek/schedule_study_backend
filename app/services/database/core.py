from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import create_engine
import os
from sqlalchemy.orm import sessionmaker
from . import base_ORM
from loguru import logger
from sqlalchemy_utils import database_exists, create_database


async def get_engine(sync=False):
    logger.debug("Получаем engine базы данных")

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
    logger.debug("Создаем сессию базы данных")
    engine = await get_engine()

    sessionmaker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with sessionmaker() as session:
        try:
            logger.debug("Возващаем генератором сессию базы данных")
            yield session
        finally:
            await session.close()


async def create_tables():
    engine = await get_engine(sync=True)

    if not database_exists(engine.url):
        create_database(engine.url)
        logger.debug("База данных успешно создана")

    logger.debug("Запускаем создание таблиц")
    base_ORM.Base.metadata.create_all(engine, checkfirst=True)
    logger.info("tables created successfully")
    return True

