import json
from ..services import database as db, rabbitmq
from loguru import logger
from aio_pika.abc import AbstractIncomingMessage
import asyncio
from . import time_utils
from .. import models
from icecream import ic
import pydantic
from app import models


async def all_cabinets():
    logger.debug("getting all cabients")

    try:
        # Open session to database
        async with await db.get_session() as session:
            async with session.begin():

                # Form query to get all teachers from database
                query = (
                    db.select(db.table.Cabinets.cabinet)
                )
                # Execute query to database
                result = await session.execute(query)

                # Getting result
                cabients = result.scalars().all()

                return {
                    "cabients": cabients
                }

    except Exception:
        logger.exception(f"ERROR getting all cabinets from database")
        return False
    


async def set_cabinet(
        cabinet: str, # example: "5а-2"
):
    logger.debug("start adding cabinet to database")

    
    try:
        # Open session to database
        async with await db.get_session() as session:
            async with session.begin():

                #checking cabinet in db
                query_check = (
                    db.select(db.table.Cabinets.cabinet)
                   .where(db.table.Cabinets.cabinet == cabinet)
                )

                result = await session.execute(query_check)

                exists_cabinet = result.scalar_one_or_none()

                if exists_cabinet:
                    query = (
                        db.update(
                            db.table.Cabinets
                        )
                        .values(
                            cabinet = cabinet, 
                        )
                    )

                else:
                    query = (
                        db.insert(db.table.Cabinets)
                        .values(cabinet=cabinet)
                    )
                await session.execute(query)
                return True

    except Exception:
        logger.exception(f"ERROR adding cabinet to database")
        return False
    
async def remove_cabinet(
        cabinet: str # example: "5а-2"
):
    
    logger.debug("start removing cabinet")

    try:
        # Open session to database
        async with await db.get_session() as session:
            async with session.begin():
                
                # checking cabinet in db

                query_check = (
                    db.select(db.table.Cabinets.cabinet)
                   .where(db.table.Cabinets.cabinet == cabinet)
                )

                result = await session.execute(query_check)

                exists_cabinet = result.scalar_one_or_none()

                if exists_cabinet:
                    query = (
                        db.delete(db.table.Cabinets)
                       .where(db.table.Cabinets.cabinet == cabinet)
                    )

                    await session.execute(query)
                    return True
                else:
                    logger.debug(f"Cabinet {cabinet} not found in database")
                    return "not found"
    
    except Exception:
        logger.exception(f"ERROR remove cabinet from database")
        return False
