from ..services import database as db
from loguru import logger
from . import time_utils
from .. import schemas
from app import schemas
from app.core.dependencies import SessionDep
from icecream import ic

from app import utils


async def get_lessons_app(
        group: str, # group example "Исп-232"
        session: SessionDep, # Сессия базы данных
) -> bool | schemas.Schedule_app_output:
    try:
        num_day, num_week = await time_utils.get_day_and_week_number()
        logger.debug(f"Успешно получили num_day: {num_day}, num_week: {num_week}")

        logger.debug("Формируем запросы на получение данных")
        query_lessons = (
            db.select(
                db.table.Lessons.id, 
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
        schedule_data = result_lessons.all()
        if not schedule_data:
            logger.debug("Пар для этой группы нет. Возвращаем пустую заготовку")
            return schedule_info

        time_data = result_time.all()
        replacements_data = result_replacements.scalars().all()

        logger.debug("Обрабатываем замены и формируем словарь")
        replacements_key = {
            (i.num_day, i.num_lesson): {
                "replace_id": i.id, 
                "item": i.item, 
                "cabinet": i.cabinet,
                "teacher": i.teacher 
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
            logger.warning("Произошла ошибка. На сегодня нет расписания. Оставляем такой же порядок")
            sorted_schedule_keys = sorted_days

        status_time = True
        for day in sorted_schedule_keys:
            logger.debug(f"Обрабатываем расписание для дня: {day}")
            lessons_in_schedule = []
            for lesson in grouped_schedule[day]:
                event_time = time_key.get((lesson.num_day, lesson.num_lesson), ["ㅤ"])
                previous_event_time = time_key.get((lesson.num_day, lesson.num_lesson - 1))
                status, time, percentage = (await time_utils.check_time_lessons(event_time, previous_event_time)
                                            if lesson.num_day == num_day else ("not active", "", 0))

                lessons_in_schedule.append({
                    "lesson_id": lesson.id,
                    "item": lesson.item,
                    "cabinet": lesson.cabinet,
                    "teacher": lesson.teacher,
                    "event_time": event_time,
                    "num_lesson": lesson.num_lesson,
                    "status": status if status_time else "not active",
                    "time": time,
                    "percentage": percentage,
                    "replace": replacements_key.get((lesson.num_day, lesson.num_lesson))
                })
                
                if status != "not active":
                    status_time = False

            final_schedule.append({
                "day": schemas.Num_to_day[day] + " (Сегодня)" if num_day == day else schemas.Num_to_day[day],
                "date": await time_utils.get_date_by_day(day),
                "lessons": lessons_in_schedule
            })


        logger.debug("Формируем pydantic model")
        schedule_info_model = schemas.Schedule_app_output(
            **schedule_info
        ).model_dump()

        logger.debug("Расписание успешно сформированно. Вовзаращем его")
        return schedule_info_model

    except Exception:
        logger.exception("Ошибка при получении расписания из базы данных")
        return False
    

    
    
    

    



async def get_lessons_teacher_app(
        teacher: str, # teacher example "Демиденко Наталья Ильинична"
        session: SessionDep, # Сессия базы данных
) -> schemas.Schedule_teacher_out | bool:
    try:
        logger.debug("Формируем запрос на получение пар для учителя")

        num_day, num_week = await time_utils.get_day_and_week_number()
        logger.debug(f"Успешно получили num_day: {num_day}, num_week: {num_week}")

        logger.debug("Формируем запросы на получение данных")
        query_lessons = (
            db.select(
                db.table.Lessons.id, 
                db.table.Lessons.item, 
                db.table.Lessons.group, 
                db.table.Lessons.num_day, 
                db.table.Lessons.num_lesson, 
                db.table.Lessons.week, 
                db.table.Lessons.teacher, 
                db.table.Lessons.cabinet
            )
            .filter_by(teacher=teacher, week=num_week)
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
            db.select(db.table.Replacements.id,
                      db.table.Replacements.num_day,
                      db.table.Replacements.num_lesson,
                      db.table.Replacements.item,
                      db.table.Replacements.teacher,
                      db.table.Replacements.cabinet,
                      db.table.Replacements.group
                      )
            .filter_by(teacher=teacher)
        )


        logger.debug("Создаём заготовку для ответа")
        final_schedule = []
        schedule_info = {
            "teacher": teacher,
            "week": num_week,
            "schedule": final_schedule
            }

        logger.debug("Выполняем запросы на получение данных")
        result_lessons = await session.execute(query_lessons)
        result_time = await session.execute(query_time)
        result_replacements = await session.execute(query_replacements)

        logger.debug("Получение результатов запросов")
        schedule_data = result_lessons.all()
        if not schedule_data:
            logger.debug("Пар для этого учителя нет. Возвращаем пустую заготовку")
            return schedule_info
        
        time_data = result_time.all()
        replacements_data = result_replacements.all()

        logger.debug("Обрабатываем замены и формируем словарь")
        replacements_key = {
            (i.num_day, i.num_lesson): {
                "replace_id": i.id,
                "item": i.item, 
                "group": i.group, 
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
            logger.warning("Произошла ошибка. На сегодня нет расписания. Оставляем такой же порядок")
            sorted_schedule_keys = sorted_days


        status_time = True
        for day in sorted_schedule_keys:
            logger.debug(f"Обрабатываем расписание для дня: {day}")
            lessons_in_schedule = []
            for lesson in grouped_schedule[day]:
                event_time = time_key.get((lesson.num_day, lesson.num_lesson), ["ㅤ"])
                previous_event_time = time_key.get((lesson.num_day, lesson.num_lesson - 1))
                status, time, percentage = (await time_utils.check_time_lessons(event_time, previous_event_time)
                                            if lesson.num_day == num_day else ("not active", "", 0))

                lessons_in_schedule.append({
                    "lesson_id": lesson.id,
                    "item": lesson.item,
                    "cabinet": lesson.cabinet,
                    "group": lesson.group,
                    "event_time": event_time,
                    "num_lesson": lesson.num_lesson,
                    "status": status if status_time else "not active",
                    "time": time,
                    "percentage": percentage,
                    "replace": replacements_key.get((lesson.num_day, lesson.num_lesson))
                })
                if status:
                    status_time = False

            final_schedule.append({
                "day": schemas.Num_to_day[day] + " (Сегодня)" if num_day == day else schemas.Num_to_day[day],
                "date": await time_utils.get_date_by_day(day),
                "lessons": lessons_in_schedule
            })
            
        logger.debug("Формирование модели pydanitc")
        
        schedule_info_model = schemas.Schedule_teacher_out(
            **schedule_info
        ).model_dump()
            

        logger.debug("Расписание успешно сформированно. Вовзаращем его")
        return schedule_info_model


    except Exception:
        logger.exception(f"Ошибка при получении расписания для учителя {teacher} из базы данных")
        return False


async def forming_schedule(schedule_data, replacements_data, num_day, num_week):
    logger.debug("Обрабатываем замены и формируем словарь")
    replacements_key = {
        (i.num_day, i.num_lesson): {
            "replace_id": i.id, 
            "item": i.item, 
            "cabinet": i.cabinet,
            "group": i.group,
            "teacher": i.teacher,
        }
        for i in replacements_data
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
        logger.warning("На сегодня нет расписания. Оставляем такой же порядок")
        sorted_schedule_keys = sorted_days
    
    final_schedule = []

    for day in sorted_schedule_keys:
        logger.debug(f"Обрабатываем расписание для дня: {day}")
        lessons_in_schedule = []
        for lesson in grouped_schedule[day]:
            lessons_in_schedule.append(
                schemas.Info_lesson(
                    lesson_id = lesson.id,
                    item = lesson.item,
                    cabinet = lesson.cabinet,
                    teacher = lesson.teacher,
                    group = lesson.group,
                    num_lesson = lesson.num_lesson,
                    replace = replacements_key.get((lesson.num_day, lesson.num_lesson))
                ).model_dump())
            
        final_schedule.append(schemas.info_day_lesson(
            day = schemas.Num_to_day[day],
            date = await utils.time_utils.get_date_by_day(day),
            lessons = lessons_in_schedule
        ).model_dump())
    return final_schedule





    
