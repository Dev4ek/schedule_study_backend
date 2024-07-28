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


async def all_teachers():
    logger.debug("getting all teachers")

    try:
        # Open session to database
        async with await db.get_session() as session:
            async with session.begin():

                # Form query to get all teachers from database
                query = (
                    db.select(db.table.Teachers.full_name)
                )

                # Execute query to database
                result = await session.execute(query)

                # Getting result
                teachers = result.scalars().all()
                

                return {
                    "teachers": teachers
                }

    except Exception:
        logger.exception(f"ERROR getting all teachers from database")
        return False
    


async def set_teacher(
        full_name: str, # example: "Демиденко Наталья Ильинична"
):
    logger.debug("start adding teacher")

    
    try:
        # Open session to database
        async with await db.get_session() as session:
            async with session.begin():

                #checking teacher in db

                query_check = (
                    db.select(db.table.Teachers.full_name)
                   .where(db.table.Teachers.full_name == full_name)
                )

                result = await session.execute(query_check)

                exists_teacher = result.scalar_one_or_none()

                if exists_teacher:
                    query = (
                        db.update(
                            db.table.Teachers
                        )
                        .values(
                            full_name = full_name, 
                            short_name = full_name
                        )
                    )

                else:
                    query = (
                        db.insert(db.table.Teachers)
                        .values(full_name=full_name, short_name=full_name)
                    )

                await session.execute(query)
                return True

    except Exception:
        logger.exception(f"ERROR adding teacher to database")
        return False
    
async def remove_teacher(
        full_name: str # example: "Демиденко Наталья Ильинична"
):
    
    logger.debug("start removing teacher")

    try:
        # Open session to database
        async with await db.get_session() as session:
            async with session.begin():
                
                # checking teacher in db

                query_check = (
                    db.select(db.table.Teachers.full_name)
                   .where(db.table.Teachers.full_name == full_name)
                )

                result = await session.execute(query_check)

                exists_teacher = result.scalar_one_or_none()

                if exists_teacher:
                    query = (
                        db.delete(db.table.Teachers)
                       .where(db.table.Teachers.full_name == full_name)
                    )

                    await session.execute(query)
                    return True
                else:
                    logger.debug(f"Teacher {full_name} not found in database")
                    return "not found"

    
    except Exception:
        logger.exception(f"ERROR remove teacher from database")
        return False
