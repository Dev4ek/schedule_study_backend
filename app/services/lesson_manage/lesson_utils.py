import json
from .. import database as db, rabbitmq
from loguru import logger
from aio_pika.abc import AbstractIncomingMessage
import asyncio
from . import time_utils
from ... import models
from icecream import ic
import pydantic
from app import models


async def set_lesson(
        lesson: models.Lesson_input, # lesson which need set
) -> bool:
    
    logger.debug("insert lesson for group: {group}")

    group = lesson.group
    num_day = models.Day_num[lesson.day]

    try:
        # open session to database
        async with await db.get_session() as session:
            async with session.begin():
                
                # checking group existence in database
                query_check = (
                    db.select(db.table.Lessons.id)
                    .filter_by(
                        group=group, 
                        num_day=num_day, 
                        num_lesson=lesson.num_lesson,
                        week=lesson.week,
                        )
                    )

                # do qeury to database
                result = await session.execute(query_check)

                # getting result
                existing_schedule = result.scalar_one_or_none()


                time_subquery = (
                        db.select(db.table.Times.time)
                        .where(db.and_(
                                db.table.Times.num_lesson==lesson.num_lesson,
                                db.table.Times.num_day==num_day
                                )
                            )
                        .limit(1)
                        .scalar_subquery()
                    )


                # if schedule exists in database, update it OR insert new group with new schedule
                if existing_schedule:
                    query = (
                        db.update(db.table.Lessons)
                        .filter_by(
                                group=group,
                                num_day=num_day,
                                num_lesson=lesson.num_lesson,
                                week=lesson.week,
                                )
                        .values(
                            item=lesson.item,
                            teacher=lesson.teacher,
                            auditory=lesson.auditory,

                            event_time=time_subquery
                            )
                    )

                # if schedule not exists in database, insert new group with new schedule
                else:

                    query = (
                        db.insert(db.table.Lessons)

                        .values(
                            num_day=num_day,
                            group=group,
                            item=lesson.item,
                            num_lesson=lesson.num_lesson,
                            teacher=lesson.teacher,
                            auditory=lesson.auditory,
                            week=lesson.week,

                            event_time=time_subquery
                            )
                    )

                # do qeury to database
                await session.execute(query)
                
                return True
    except Exception:
        logger.exception(f"ERROR setting schedule to database")
        return False






async def get_lessons(
        group: str, # group example "Исп-232"
        reply_to: AbstractIncomingMessage, # rabbit queue name where to send response
) -> bool:
    logger.debug("getting schedule for group: {group}")

    try:
        # Open session to database
        async with await db.get_session() as session:
            async with session.begin():

                num_day, num_week = await time_utils.get_day_and_week_number()

                # Form query to get schedule from database
                query = (
                    db.select(
                        db.table.Lessons.item, 
                        db.table.Lessons.num_day, 
                        db.table.Lessons.num_lesson, 
                        db.table.Lessons.week, 
                        db.table.Lessons.teacher, 
                        db.table.Lessons.auditory, 
                        db.table.Lessons.event_time
                    )
                    .filter_by(group=group)
                    .order_by(db.table.Lessons.num_day.asc(), db.table.Lessons.num_lesson.asc())                 
                )

                # Execute query to database
                result = await session.execute(query)

                # Getting result
                schedule_data: list[models.Lesson_in_db] = result.all()

                # If schedule does not exist, return false
                if not schedule_data:
                    logger.info(f"schedule not in database for group: {group}")
                    return False

                # Group lessons by days
                grouped_schedule = {}
                for lesson in schedule_data:
                    if lesson.num_day not in grouped_schedule:
                        grouped_schedule[lesson.num_day] = []
                    grouped_schedule[lesson.num_day].append(lesson)

                # Sort schedule data by current day
                sorted_days = sorted(grouped_schedule.keys())
                index = sorted_days.index(num_day)
                sorted_schedule_keys = sorted_days[index:] + sorted_days[:index]

                # Generate schedule
                final_schedule = []
                for day in sorted_schedule_keys:
                    lessons = grouped_schedule[day]
                    
                    schedule = {
                                "day": models.Num_day[day] + " (Сегодня)" if num_day == day else models.Num_day[day],
                                "date": "---",  # Finish the task...
                                "lessons": [
                                    {
                                        "item": lesson.item + f" ({lesson.auditory})",
                                        "teacher": lesson.teacher,
                                        "event_time": [lesson.event_time],
                                        "active": False,
                                        "time": ""
                                    }
                                    for lesson in lessons
                                ]
                            }
                    
                    final_schedule.append(schedule)


                schedule_info = {
                    "group": group,
                    "week": num_week,
                    "schedule": final_schedule
                }



                final_schedule_str = json.dumps(schedule_info)

                logger.info(f"lessons exists in database for group: {group}")

                await rabbitmq.response_in_queue_schedule(final_schedule_str, reply_to)

                return True
            

                
    except Exception:
        logger.exception(f"ERROR getting schedule from database")
        return False
