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

                async def set_lesson_in_db(num_week):
                    # checking group existence in database
                    query_check = (
                        db.select(db.table.Lessons.id)
                        .filter_by(
                            group=group, 
                            num_day=num_day, 
                            num_lesson=lesson.num_lesson,
                            week=num_week,
                            )
                        )

                    # do qeury to database
                    result = await session.execute(query_check)

                    # getting result
                    existing_schedule = result.scalar_one_or_none()

                    # if schedule exists in database, update it OR insert new group with new schedule
                    if existing_schedule:
                        query = (
                            db.update(db.table.Lessons)
                            .filter_by(
                                    group=group,
                                    num_day=num_day,
                                    num_lesson=lesson.num_lesson,
                                    week=num_week,
                                    )
                            .values(
                                item=lesson.item,
                                teacher=lesson.teacher,
                                auditory=lesson.auditory,
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
                                week=num_week,
                                )
                        )

                    # do qeury to database
                    await session.execute(query)



                if lesson.week == 0:
                    for week in range(1, 3):
                        await set_lesson_in_db(week)
                else:
                    await set_lesson_in_db(lesson.week)

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
                query_lessons = (
                    db.select(
                        db.table.Lessons.item, 
                        db.table.Lessons.num_day, 
                        db.table.Lessons.num_lesson, 
                        db.table.Lessons.week, 
                        db.table.Lessons.teacher, 
                        db.table.Lessons.auditory, 
                    )
                    .filter_by(group=group, week=num_week)
                    .order_by(db.table.Lessons.num_day.asc(), db.table.Lessons.num_lesson.asc())                 
                )

                query_time = (
                    db.select(
                        db.table.Times.time, 
                        db.table.Times.num_lesson, 
                        db.table.Times.num_day
                    )
                    .order_by(db.table.Times.num_day.asc(), db.table.Times.num_lesson.asc())                 
                )


                # Execute query to database
                result_lessons  = await session.execute(query_lessons)
                result_time  = await session.execute(query_time)

                # Getting result
                schedule_data: list[models.Lesson_in_db] = result_lessons.all()

                # Getting result
                time_data = result_time.all()

                time_key = {}
                for i in time_data:
                    time_key[(i.num_day, i.num_lesson)] = i.time.split(', ')

                # Generate schedule
                final_schedule = []

                schedule_info = {
                    "group": group,
                    "week": num_week,
                    "schedule": final_schedule
                }


                # If schedule does not exist, return false
                if not schedule_data:
                    logger.info(f"schedule not in database for group: {group}")

                    await rabbitmq.response_in_queue_schedule(json.dumps(schedule_info), reply_to)
                    return False

                # Group lessons by days
                grouped_schedule = {}
                for lesson in schedule_data:
                    if lesson.num_day not in grouped_schedule:
                        grouped_schedule[lesson.num_day] = []
                    grouped_schedule[lesson.num_day].append(lesson)

                try:
                    # Sort schedule data by current day
                    sorted_days = sorted(grouped_schedule.keys())
                    index = sorted_days.index(num_day)
                    sorted_schedule_keys = sorted_days[index:] + sorted_days[:index]
                except Exception:
                    sorted_schedule_keys = sorted_days

                status_time = True

                for day in sorted_schedule_keys:
                    lessons = grouped_schedule[day]

                    lessons_in_schedule = []

                    for lesson in lessons:
                        try:
                            event_time = time_key[(lesson.num_day, lesson.num_lesson)]

                            if lesson.num_day is num_day:
                                status, time = await time_utils.check_time_lessons(event_time)
                            else:
                                status, time = False, ""

                        except KeyError:
                            event_time = [""]
                            status, time = False, ""



                        lessons_in_schedule.append({
                                        "item": lesson.item + f" ({lesson.auditory})",
                                        "teacher": lesson.teacher,
                                        "event_time": event_time,
                                        "status": status if status_time else None,
                                        "time": time
                                    })
                        if status:
                            status_time = False
                        

                    schedule = {
                                "day": models.Num_day[day] + " (Сегодня)" if num_day == day else models.Num_day[day],
                                "date": await time_utils.get_date_by_day(day),
                                "lessons": lessons_in_schedule
                            }
                    final_schedule.append(schedule)


                final_schedule_str = json.dumps(schedule_info)

                logger.success(f"get schedule successfully: {group}")

                await rabbitmq.response_in_queue_schedule(final_schedule_str, reply_to)

                return True
            

                
    except Exception:
        logger.exception(f"ERROR getting schedule from database")
        return False
