from ..services import database as db
from loguru import logger
from . import time_utils
from .. import schemas
from app import schemas
from app.core.dependencies import SessionDep
from icecream import ic


async def get_lessons(
        group: str, # group example "Исп-232"
        session: SessionDep, # Сессия базы данных
) -> bool | schemas.Schedule_output:
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
        schedule_info_model = schemas.Schedule_output(
            **schedule_info
        ).model_dump()

        logger.debug("Расписание успешно сформированно. Вовзаращем его")
        return schedule_info_model

    except Exception:
        logger.exception("Ошибка при получении расписания из базы данных")
        return False


async def get_lessons_teacher(
        teacher: str, # teacher example "Демиденко Наталья Ильинична"
        session: SessionDep, # Сессия базы данных
) -> schemas.Schedule_tacher_output | bool:
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
        
        schedule_info_model = schemas.Schedule_tacher_output(
            **schedule_info
        ).model_dump()
            

        logger.debug("Расписание успешно сформированно. Вовзаращем его")
        return schedule_info_model


    except Exception:
        logger.exception(f"Ошибка при получении расписания для учителя {teacher} из базы данных")
        return False

async def put_lesson(
    payload: schemas.Lesson_input, # Схема установки расписания
    session: SessionDep, # Сессия базы данных
) -> bool:
    
    group = payload.group
    num_day = schemas.Day_to_num[payload.day]

    # функция для замены или установки расписания
    async def _upsert_lesson(num_week):
        logger.debug("Формируем запрос на существование пары в дб")
        query_check = (
            db.select(db.table.Lessons.id)
            .filter_by(
                group=group,
                num_day=num_day,
                num_lesson=payload.num_lesson,
                week=num_week,
            )
        )

        logger.debug("Выполняем запрос в базу данных для проверки существования пары")
        result = await session.execute(query_check)

        logger.debug("Получаем результат scalar_one_or_none")
        existing_schedule = result.scalar_one_or_none()

        if existing_schedule:
            logger.debug("Пара найдена в базе данных. Формируем запрос на обновление данных пары")
            query = (
                db.update(db.table.Lessons)
                .filter_by(
                    group=group,
                    num_day=num_day,
                    num_lesson=payload.num_lesson,
                    week=num_week,
                )
                .values(
                    item=payload.item,
                    teacher=payload.teacher,
                    cabinet=payload.cabinet,
                )
            )
        else:
            logger.debug("Пара не найдена в базе данных. Формируем запрос на добавление пары")
            query = (
                db.insert(db.table.Lessons)
                .values(
                    num_day=num_day,
                    group=group,
                    item=payload.item,
                    num_lesson=payload.num_lesson,
                    teacher=payload.teacher,
                    cabinet=payload.cabinet,
                    week=num_week,
                )
            )

        logger.debug("Выполняем запрос в базу данных")
        await session.execute(query)

    try:
        if payload.week == 0:
            logger.debug("Устанавливаем пару для двух недель")
            for week in range(1, 3):
                logger.debug(f"Устанавливаем расписание на неделю {week}")
                await _upsert_lesson(week)
        else:
            logger.debug(f"Устанавливаем расписание на указанную неделю {payload.week}")
            await _upsert_lesson(payload.week)

        await session.commit()

        logger.debug("Пара была установлена. Возвращаем True")
        return True
    except Exception as e:
        logger.exception("Ошибка при установке пары в базу данных")
        return False



async def remove_lesson(
        payload: schemas.Remove_lesson,
        session: SessionDep, # Сессия базы данных
):

    num_day: int = schemas.Day_to_num[payload.day]

    try:
        # функция для удаления пары 
        async def _removing_lessons(_num_week):
            logger.debug(f"Формируем запрос на удалеине пары где num_week = {_num_week}")
            query_check = (
                    db.delete(db.table.Lessons)
                    .filter_by(
                        group=payload.group, 
                        num_day=num_day, 
                        num_lesson=payload.num_lesson,
                        week=_num_week,
                        )
                    )

            logger.debug("Делаем запрос в бд")
            await session.execute(query_check)


        if payload.week == 0:
            for week in range(1, 3):
                await _removing_lessons(week)
        else:
            await _removing_lessons(payload.week)

        await session.commit()

        logger.debug("Успешно удалено. Возвращаем True")
        return True

    except Exception:
        logger.exception(f"Произошла ошибка при удалении пары")
        return False
    
    
async def get_lesson_by_id(
    lesson_id: int,
    session: SessionDep, # Сессия базы данных
):
    try:
        logger.debug(f"Выполняем запрос в бд просмотр информации о паре")

        result = await session.execute(
            db.select(db.table.Lessons.__table__)
            .filter_by(
                id=lesson_id,
            ))

        data_lesson = result.one_or_none()

        if data_lesson:
            logger.debug("Пара найдена. Делаем запрос чтобы узнать время проведения пары")
            
            result_time = await session.execute(
                db.select(db.table.Times.time)
                .filter_by(
                    num_day=data_lesson.num_day,
                    num_lesson=data_lesson.num_lesson,
                ))
            
            logger.debug("Получаем данные о времени")
            data_time = result_time.scalar_one_or_none()
            
            logger.debug("Делаем запрос в бд для просмотра замен на пару")
            result_replacements = await session.execute(
                db.select(db.table.Replacements.__table__)
                .filter_by(
                    num_day=data_lesson.num_day,
                    num_lesson=data_lesson.num_lesson,
                    group=data_lesson.group
                )
            )
            
            replacement_data = result_replacements.first()
            
            form_replace = {
                    "replace_id": replacement_data.id,
                    "item": replacement_data.item,
                    "cabinet": replacement_data.cabinet,
                    "teacher": replacement_data.teacher,
                } if replacement_data else None
            
            
            logger.debug("Формируем модель pydantic и возвращаем её")
            return schemas.Info_lesson_output(
                    lesson_id=data_lesson.id,
                    item=data_lesson.item,
                    teacher=data_lesson.teacher,
                    cabinet=data_lesson.cabinet,
                    group=data_lesson.group,
                    num_lesson=data_lesson.num_lesson,
                    day=schemas.Num_to_day[data_lesson.num_day],
                    event_time=data_time.split(", ") if data_time else ["ㅤ"],
                    replace=form_replace
                ).model_dump()
        else:
            logger.debug("Пара не найдена. Возвращаем not found")
            return "not found"
    except Exception:
        logger.exception(f"Произошла ошибка при удалении пары")
        return False
    