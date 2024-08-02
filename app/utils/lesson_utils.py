import json
from ..services import database as db
from loguru import logger
from aio_pika.abc import AbstractIncomingMessage
import asyncio
from . import time_utils
from .. import schemas
from icecream import ic
import pydantic
from app import schemas
from app.core.dependencies import SessionDep





async def set_lesson(
        lesson: schemas.Lesson_input, # lesson which need set
):
    
    logger.debug("insert lesson for group: {group}")

    group = lesson.group
    num_day = schemas.Day_num[lesson.day]

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
                                cabinet=lesson.cabinet,
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
                                cabinet=lesson.cabinet,
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
        session: SessionDep, # Сессия базы данных
) -> bool:
    try:
        logger.debug("Получаем сегодняшний день и номер недели 1 или 2")
        num_day, num_week = await time_utils.get_day_and_week_number()
        logger.debug(f"Успешно получили num_day: {num_day}, num_week: {num_week}")

        logger.debug("Формируем запросы на получение данных")
        query_lessons = (
            db.select(
                db.table.Lessons.item, 
                db.table.Lessons.num_day, 
                db.table.Lessons.num_lesson, 
                db.table.Lessons.week, 
                db.table.Lessons.teacher, 
                db.table.Lessons.cabinet
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

        query_replacements = (
            db.select(db.table.Replacements)
            .filter_by(group=group)
        )


        logger.debug("Создаём заготовку для ответа")
        final_schedule = []
        schedule_info = {
            "group": group,
            "week": num_week,
            "schedule": final_schedule
            }

        logger.debug("Выполняем запросы на получение данных")
        result_lessons = await session.execute(query_lessons)
        result_time = await session.execute(query_time)
        result_replacements = await session.execute(query_replacements)

        logger.debug("Получение результатов запросов")
        schedule_data: list[schemas.Lesson_in_db] = result_lessons.all()
        if not schedule_data:
            logger.debug("Пар для этой группы нет. Возвращаем пустую заготовку")
            return schedule_info

        time_data = result_time.all()
        replacements_data = result_replacements.scalars().all()

        logger.debug("Обрабатываем замены и формируем словарь")
        replacements_key = {

            (i.num_day, i.num_lesson): {
                "item": i.item, 
                "teacher": i.teacher, 
                "cabinet": i.cabinet
            }
            for i in replacements_data
        }

        logger.debug("Обрабатываем время и формируем словарь")
        time_key = {
            (i.num_day, i.num_lesson): i.time.split(', ')
            for i in time_data
        }

        logger.debug("Группируем пары по дням")
        grouped_schedule = {}
        for lesson in schedule_data:
            grouped_schedule.setdefault(lesson.num_day, []).append(lesson)

        logger.debug("Сортируем расписание по дням, начиная с текущего дня")
        sorted_days = sorted(grouped_schedule.keys())
        try:
            index = sorted_days.index(num_day)
            sorted_schedule_keys = sorted_days[index:] + sorted_days[:index]
        except ValueError:
            logger.warning("Произошла ошибка. Оставляем такой же порядок")
            sorted_schedule_keys = sorted_days

        status_time = True
        for day in sorted_schedule_keys:
            logger.debug(f"Обрабатываем расписание для дня: {day}")
            lessons_in_schedule = []
            for lesson in grouped_schedule[day]:
                event_time = time_key.get((lesson.num_day, lesson.num_lesson), [""])
                previous_event_time = time_key.get((lesson.num_day, lesson.num_lesson - 1))
                status, time, percentage = (await time_utils.check_time_lessons(event_time, previous_event_time)
                                            if lesson.num_day == num_day else (False, "", 0))

                lessons_in_schedule.append({
                    "item": lesson.item,
                    "cabinet": lesson.cabinet,
                    "teacher": lesson.teacher,
                    "event_time": event_time,
                    "status": status if status_time else None,
                    "time": time,
                    "percentage": percentage,
                    "replace": replacements_key.get((lesson.num_day, lesson.num_lesson))
                })
                if status:
                    status_time = False

            final_schedule.append({
                "day": schemas.Num_day[day] + " (Сегодня)" if num_day == day else schemas.Num_day[day],
                "date": await time_utils.get_date_by_day(day),
                "lessons": lessons_in_schedule
            })


        logger.debug("Расписание успешно сформированно. Вовзаращем его")
        return final_schedule

    except Exception:
        logger.exception("Ошибка при получении расписания из базы данных")
        return False


async def remove_lesson(
        group: str, # example "Исп-232"
        day: str, # example "Понедельник"
        num_lesson: int, # num lesson example 1 or 2 or 3...
        num_week: int
):

    logger.debug(f"Removing lesson for group: {group} day: {day}, lesson_number: {num_lesson}")

    num_day: int = schemas.Day_num[day]

    try:

        # Open session to database
        async with await db.get_session() as session:
            async with session.begin():

                async def _removing_lessons(_num_week):
                    # checking group existence in database
                    query_check = (
                            db.delete(db.table.Lessons)
                            .filter_by(
                                group=group, 
                                num_day=num_day, 
                                num_lesson=num_lesson,
                                week=_num_week,
                                )
                            )

                    # do qeury to database
                    await session.execute(query_check)


                if num_week == 0:
                    for week in range(1, 3):
                        await _removing_lessons(week)
                else:
                    await _removing_lessons(week)

                return True

    except Exception:
        logger.exception(f"ERROR removing lesson from database")
        return False