import json
from .. import database as db, rabbitmq
from loguru import logger
from aio_pika.abc import AbstractIncomingMessage
import asyncio
from . import time_utils

async def get_schedule(
        group: str, # group example "Исп-232"
        reply_to: AbstractIncomingMessage, # rabbit queue name where to send response
) -> bool:
    logger.debug("getting schedule for group: {group}")

    try:
        # open session to database
        async with await db.get_session() as session:
            async with session.begin():

                # form qery to get schedule from database
                query = (
                    db.select(db.table.Schedule.schedule)
                    .filter_by(group=group)
                    .limit(1)
                )

                # do qeury to database
                result = await session.execute(query)

                # getting result
                schedule = result.scalars().first()  

                # if schedule exists in database, send it to rabbitmq and return True
                if schedule:
                    logger.info(f"schedule exists in database for group: {group}")

                    await rabbitmq.response_in_queue_schedule(schedule, reply_to)

                    return True

                else:
                    logger.info(f"schedule not in database for group: {group}")
                    
                    return False
                
    except Exception as e:
        logger.exception(f"ERROR getting schedule from database: {e}")
        return False


async def set_schedule(
        group: str, # group example "Исп-232"
        schedule: dict, # schedule which need set
        num_lesson: int # number lesson example 1 or 2 or 3...
) -> bool:
    
    logger.debug("insert schedule for group: {group}")

    try:
        # open session to database
        async with await db.get_session() as session:
            async with session.begin():
                
                # checking group existence in database
                query_check = db.select(db.table.Schedule).where(
                    db.and_(
                            db.table.Schedule.group == group,
                            db.table.Schedule.num_lesson == num_lesson,
                            )
                        )

                # do qeury to database
                result = await session.execute(query_check)

                # getting result
                existing_schedule = result.scalar_one_or_none()

                # convert json schedule to string format
                schedule_str = json.dumps(schedule)
                
                # if schedule exists in database, update it OR insert new group with new schedule
                if existing_schedule:
                    query = (
                        db.update(db.table.Schedule)
                        .where(db.table.Schedule.group == group)
                        .values(schedule=schedule_str)
                    )
                else:
                    query = (
                        db.insert(db.table.Schedule)
                        .values(
                            group=group, 
                            schedule=schedule_str,
                            num_lesson=num_lesson
                            )
                    )
                # do qeury to database
                await session.execute(query)

                # commit changes in database
                await session.commit()
                
                return True
    except Exception as e:
        logger.exception(f"ERROR setting schedule to database: {e}")
        return False
