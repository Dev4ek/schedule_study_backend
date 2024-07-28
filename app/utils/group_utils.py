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


async def all_groups():
    logger.debug("getting all groups")

    try:
        # Open session to database
        async with await db.get_session() as session:
            async with session.begin():

                # Form query to get all groups from database
                query = (
                    db.select(db.table.Groups.group)
                )

                # Execute query to database
                result = await session.execute(query)

                # Getting result
                groups = result.scalars().all()

                return {
                    "groups": groups
                }

    except Exception:
        logger.exception(f"ERROR getting all groups from database")
        return False
    


async def set_group(
        group: str, # example: "Исп-232"
):
    logger.debug("start adding group")

    
    try:
        # Open session to database
        async with await db.get_session() as session:
            async with session.begin():

                #checking group in db
                query_check = (
                    db.select(db.table.Groups.group)
                   .where(db.table.Groups.group == group)
                )

                result = await session.execute(query_check)
                exists_group = result.scalar_one_or_none()

                if exists_group:
                    query = (
                        db.update(
                            db.table.Groups
                        )
                        .values(
                            group = group, 
                        )
                    )

                else:
                    query = (
                        db.insert(db.table.Groups)
                        .values(group=group)
                    )

                await session.execute(query)
                return True

    except Exception:
        logger.exception(f"ERROR adding group to database")
        return False
    
async def remove_group(
        group: str # example: "Исп-232"
):
    
    logger.debug("start removing group")

    try:
        # Open session to database
        async with await db.get_session() as session:
            async with session.begin():
                
                # checking group in db

                query_check = (
                    db.select(db.table.Groups.group)
                   .where(db.table.Groups.group == group)
                )

                result = await session.execute(query_check)
                exists_group = result.scalar_one_or_none()

                if exists_group:
                    query = (
                        db.delete(db.table.Groups)
                       .where(db.table.Groups.group == group)
                    )
                    await session.execute(query)
                    return True
                else:
                    logger.debug(f"Group {group} not found in database")
                    return "not found"

    except Exception:
        logger.exception(f"ERROR remove group from database")
        return False
