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
                
    except Exception:
        logger.exception(f"ERROR getting schedule from database")
        return False


async def set_schedule(
        group: str, # group example "Исп-232"
        schedule: dict, # schedule which need set
        num_day: int, # day example Понедельник - 1, Вторник - 2,...
        today: bool, # if True, then schedule for today
        tomorrow: bool # if True, then schedule for tomorrow
) -> bool:
    
    logger.debug("insert schedule for group: {group}")

    try:
        # open session to database
        async with await db.get_session() as session:
            async with session.begin():
                
                # checking group existence in database
                query_check = (
                    db.select(db.table.Schedule)
                    .filter_by(group=group, num_day=num_day)
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
                        .filter_by(group=group, num_day=num_day)
                        .values(schedule=schedule_str, today=today, tomorrow=tomorrow)
                    )

                # if schedule not exists in database, insert new group with new schedule
                else:

                    # get time lessons for current day
                    time_lessons_dict = await time_utils.time_for_lessons(num_day)

                    query = (
                        db.insert(db.table.Schedule)
                        .values(
                            group=group, 
                            schedule=schedule_str,
                            num_day=num_day,
                            today=today,
                            tomorrow=tomorrow,

                            time_0=time_lessons_dict["time_0"],
                            time_1=time_lessons_dict["time_1"],
                            time_2=time_lessons_dict["time_2"],
                            time_3=time_lessons_dict["time_3"],
                            time_4=time_lessons_dict["time_4"]
                            )
                    )

                # do qeury to database
                await session.execute(query)

                # commit changes in database
                await session.commit()
                
                return True
    except Exception:
        logger.exception(f"ERROR setting schedule to database")
        return False
