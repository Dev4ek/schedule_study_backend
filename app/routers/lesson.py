from typing import Optional
from fastapi import APIRouter, Depends, Path, Query, Body
from fastapi.responses import JSONResponse
from ..core import dependencies
from ..services import redis
from .. import schemas, utils
from loguru import logger
from app.core.dependencies import SessionDep
from app.services import database as db
from icecream import ic

router_lesson = APIRouter(prefix="/lesson", tags=["Расписание"])


@router_lesson.get(
        path="/group",
        summary="Посмотреть пары для группы с заменами",
        response_model=schemas.Schedule_group_out
)
async def check_lessons_group(
    session: SessionDep, # Сессия базы данных
    group: str = Query(..., description="Группа", example="Исп-232"),
    num_week: Optional[int] = Query(None, description="НЕОБЯЗАТЕЛЬНО Номер недели", example="2",ge=1, le=2)
) -> JSONResponse: 
    logger.info(f"Запрос на получение пар для группы с заменами")
    
    num_week_ = num_week

    num_day, num_week = await utils.time_utils.get_day_and_week_number()
    logger.debug(f"Успешно получили num_day: {num_day}, num_week: {num_week}")

    num_week = num_week_ or num_week

    logger.debug("Выполняем запросы в бд")
    result_lessons = await session.execute(
                    db.select(
                        db.table.Lessons
                    )
                    .filter(db.table.Lessons.group == group,
                            db.table.Lessons.week == num_week,
                            db.table.Lessons.num_lesson != 0)
                    .order_by(db.table.Lessons.num_day.asc(), db.table.Lessons.num_lesson.asc())
    )
    
    schedule_data = result_lessons.scalars().all()
    
    logger.debug("Создаём заготовку для ответа pydantic model")
    schedule_info = {
        "group": group,
        "week": num_week,
        "schedule": []
    }
    
    if not schedule_data:
        logger.debug("Пар для этой группы нет. Возвращаем пустую модель pydantic")
        schedule_info = schemas.Schedule_group_out(**schedule_info)
        return JSONResponse(content=schedule_info.model_dump(), status_code=200)

    
    logger.debug("Делаем запрос в бд замены")
    result_date = await session.execute(db.select(db.table.Depends.date_replacements))
    date = result_date.scalar()
    result_replacements = await session.execute(
                    db.select(db.table.Replacements)
                    .filter_by(
                        group=group,
                        date=date)
    )
    replacements_data = result_replacements.all()
    
    shedule_list = await utils.forming_schedule(schedule_data, replacements_data, num_day, num_week)
    schedule_info["schedule"] = shedule_list
    
    schedule_info = schemas.Schedule_group_out(**schedule_info)

    logger.debug("Расписание успешно сформированно. Вовзаращем его")
    return JSONResponse(content=schedule_info.model_dump(), status_code=200)





@router_lesson.get(
        path="/teacher",
        summary="Посмотреть пары для учителя с заменами",
        response_model=schemas.Schedule_group_out
)
async def check_lessons_teacher(
    session: SessionDep, # Сессия базы данных
    teacher: str = Query(..., description="Учитель", example="Демиденко Наталья Ильинична"),
    num_week: Optional[int] = Query(None, description="НЕОБЯЗАТЕЛЬНО Номер недели", example="2",ge=1, le=2)
) -> JSONResponse: 
    logger.info(f"Запрос на получение пар для для учителя с заменами")

    num_week_ = num_week
    num_day, num_week = await utils.time_utils.get_day_and_week_number()
    logger.debug(f"Успешно получили num_day: {num_day}, num_week: {num_week}")
    num_week = num_week_ or num_week
    
    logger.debug("Выполняем запросы в бд")
    result_lessons = await session.execute(
            db.select(
                db.table.Lessons
            )
            .filter_by(teacher=teacher, week=num_week)
            .order_by(db.table.Lessons.num_day.asc(), db.table.Lessons.num_lesson.asc())
    )

    schedule_data = result_lessons.scalars().all()
    
    logger.debug("Создаём заготовку для ответа расписания")
    schedule_info = {
        "teacher": teacher,
        "week": num_week,
        "schedule": []
        }
    
    if not schedule_data:
        logger.debug("Пар для этого учителя нет. Возвращаем пустую заготовку")
        schedule_info = schemas.Schedule_teacher_out(**schedule_info)
        return JSONResponse(content=schedule_info.model_dump(), status_code=200)
      
    logger.debug("Делаем запрос в бд замены")
    result_replacements = await session.execute(
            db.select(db.table.Replacements)
            .filter_by(teacher=teacher)
    )
    
    replacements_data = result_replacements.scalars().all()

    shedule_list = await utils.forming_schedule(schedule_data, replacements_data, num_day, num_week)
    schedule_info["schedule"] = shedule_list
    ic(schedule_info)
    
    
    logger.debug("Формирование модели pydanitc")
    schedule_info_model = schemas.Schedule_teacher_out(**schedule_info)
        
    return JSONResponse(content=schedule_info_model.model_dump(), status_code=200)










@router_lesson.get(
        path="/check",
        summary="Посмотреть установлена ли пара",
        response_model=schemas.Check_setted_output
)
async def check_setted_lesson(
    session: SessionDep, # Сессия базы данных
    day: schemas.Days = Query(..., description="День недели", example="Понедельник"),
    num_lesson: int = Query(..., description="Номер пары", example=1),
    cabinet: str = Query(..., description="Кабинет", example="405-1"),
    week: int = Query(..., description="Неделя", example=1)
) -> JSONResponse: 
    
    payload = schemas.Lesson_check_in(day=day, num_lesson=num_lesson, cabinet=cabinet, week=week)
    
    logger.info(f"Запрос на получение проверку стоит ли пара. Payload: {payload.model_dump_json()}")

    logger.debug("Выполняем запрос в бд для проверки установленных пар")
    lesson = await session.execute(
                    db.select(db.table.Lessons.__table__)
                    .filter_by(
                        cabinet=payload.cabinet,
                        num_day=schemas.Day_to_num[payload.day],
                        num_lesson=payload.num_lesson,
                        week=payload.week,
                    )
    )

    logger.debug("Получаем данные о парах")
    data_lesson = lesson.first()

    logger.debug("Формируем модель pydantic и возвращаем её")
    if data_lesson != None:
        setted_model = schemas.Check_setted_output(
                        use=True,
                        lesson=schemas.Info_setted_lessons_output(
                            lesson_id = data_lesson.id,
                            item = data_lesson.item,
                            teacher = data_lesson.teacher,
                            cabinet = data_lesson.cabinet,
                            group = data_lesson.group,
                            num_lesson = data_lesson.num_lesson,
                            week = data_lesson.week,
                            day = schemas.Num_to_day[data_lesson.num_day]
                        )
            )
    else:
        setted_model = schemas.Check_setted_output(
                        use=False,
                        lesson=None
            )
    
    return JSONResponse(content=setted_model.model_dump(), status_code=200)
        

    
    
    
    
    

@router_lesson.get(
        path="/{lesson_id}",
        summary="Посмотреть информацию о паре по айди",
        response_model=schemas.Info_lesson_output
)
async def get_lesson_by_id(
    session: SessionDep, # Сессия базы данных
    lesson_id: int = Path(..., description="Айди пары", example=11)
) -> JSONResponse: 
    logger.info(f"Запрос на получение информации о паре по айди. Айди {lesson_id}")

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
            
        logger.debug("Делаем запрос в бд замены")
        result_date = await session.execute(db.select(db.table.Depends.date_replacements))
        date = result_date.scalar()
    
        result_replacements = await session.execute(
            db.select(db.table.Replacements)
            .filter_by(
                num_day=data_lesson.num_day,
                num_lesson=data_lesson.num_lesson,
                group=data_lesson.group,
                date=date
            )
        )
        
        replacement_data = result_replacements.scalar()
        
        form_replace = {
                "replace_id": replacement_data.id,
                "item": replacement_data.item,
                "cabinet": replacement_data.cabinet,
                "teacher": replacement_data.teacher,
            } if replacement_data else None
        
        
        logger.debug("Формируем модель pydantic и возвращаем её")
        lesson_model = schemas.Info_lesson_output(
                lesson_id=data_lesson.id,
                item=data_lesson.item,
                teacher=data_lesson.teacher,
                cabinet=data_lesson.cabinet,
                group=data_lesson.group,
                num_lesson=data_lesson.num_lesson,
                week=data_lesson.week,
                day=schemas.Num_to_day[data_lesson.num_day],
                event_time=data_time.split(", ") if data_time else ["ㅤ"],
                replace=form_replace
            )
        return JSONResponse(content=lesson_model.model_dump(), status_code=200)
    else:
        logger.debug("Пара не найдена. Возвращаем not found")
        return JSONResponse(content={"message": "Пара не найдена"}, status_code=404)
    





@router_lesson.post(
        path="",
        summary="Установить или изменить пару",
        responses={
            200: {
                "description": "Успешная установка",
                "content": {
                    "application/json": {
                        "example": 
                           {
                             "message": "Пара для группы успешно установлена"                               
                           }
                    }
                },
            },
        }
)
async def set_lesson(
    session: SessionDep, # Сессия базы данных
    payload: schemas.Lesson_input = Body(..., description="Данные для добавления пары",
    example={
        "group": "Исп-232",
        "day": "Понедельник",
        "item": "Русский язык",
        "num_lesson": 2,
        "teacher": "Вартабедьян Виктория Борисовна",
        "cabinet": "405-1",
        "week": 0
    }
),
) -> JSONResponse: 
    logger.info(f"Запрос на установку расписания. Payload: {payload.model_dump_json()}")

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
                .returning(db.table.Lessons.id)
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
                .returning(db.table.Lessons.id)
            )

        logger.debug("Выполняем запрос в базу данных")
        await session.execute(query)

    if payload.week == 0:
        logger.debug("Устанавливаем пару для двух недель")
        for week in range(1, 3):
            logger.debug(f"Устанавливаем расписание на неделю {week}")
            await _upsert_lesson(week)
    else:
        logger.debug(f"Устанавливаем расписание на указанную неделю {payload.week}")
        await _upsert_lesson(payload.week)

    await session.commit()

    return JSONResponse(content={'message': "Пара для группы успешно установлена"}, status_code=200)






@router_lesson.delete(
        path="/all",
        summary="Удалить все пары",
        description="Все пары удалены - True"
     
)
async def remove_all_lesson(
    session: SessionDep, # Сессия базы данных
) -> JSONResponse: 
    logger.info(f"Запрос на удаление всех пар")

  
    logger.debug("Делаем запрос в бд на удаление всех пар")
    await session.execute(db.delete(db.table.Lessons))
    await session.commit()

    logger.info("Успешно удалено. Возвращаем True")
    return JSONResponse(content=True, status_code=200)



@router_lesson.delete(
        path="",
        summary="Удалить пару",
)
async def remove_lesson(
    session: SessionDep, # Сессия базы данных
    payload: schemas.Remove_lesson = Body(..., description="Данные для удаления пары",
    example={
        "group": "Исп-232",
        "day": "Понедельник",
        "num_lesson": 0,
        "week": 0
    })
) -> JSONResponse: 
    logger.info(f"Запрос на удаление пары. Payload: {payload.model_dump_json()}")

    num_day: int = schemas.Day_to_num[payload.day]

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

    logger.info("Успешно удалено. Возвращаем True")
    return JSONResponse(content=True, status_code=200)

    
    

@router_lesson.delete(
        path="/{lesson_id}",
        summary="Удалить пару по айди",
        responses={
            200: {
                "description": "Успешное удаление",
                "content": {
                    "application/json": {
                        "example": 
                           {
                            "message": "Пара успешно удалена"                               
                           }
                    }
                },
            },
           
        }
)
async def remove_lesson(
    session: SessionDep, # Сессия базы данных
    lesson_id: int = Path(..., description="Айди пары", example=21)
) -> JSONResponse: 
    logger.info(f"Запрос на удаление пары. lesson_id: {lesson_id}")
    
    logger.debug(f"Формируем и выполняем запрос в дб на удаление")
    await session.execute(db.delete(db.table.Lessons).filter_by(id=lesson_id))
    await session.commit()

    logger.info(f"Отдаём ответ. Пара успешно удалена")
    return JSONResponse(content={'message': "Пара успешно удалена"}, status_code=200)
