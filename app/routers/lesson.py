from fastapi import APIRouter, Depends, Path, Query, Body
from fastapi.responses import JSONResponse
from ..core import dependencies
from ..services import redis
from .. import schemas, utils
from loguru import logger
from app.core.dependencies import SessionDep


router_lesson = APIRouter(prefix="/lesson", tags=["Расписание"])

@router_lesson.get(
        path="/app", 
        dependencies=[Depends(dependencies.verify_version)],
        description="Посмотреть все расписание для группы (ДЛЯ ПРИЛОЖЕНИЯ)",
        response_model=schemas.Schedule_output,

        responses={
            200: {
                "description": "Получен список",
                "content": {
                    "application/json": {
                        "example": 
                            [
                                {
                                    "day": "Понедельник",
                                    "date": "5 Августа",
                                    "lessons": [
                                        {
                                            "item": "Классный час",
                                            "cabinet": "405-1",
                                            "teacher": "Демиденко Н.И.",
                                            "event_time": [
                                                "8:30 - 9:15",
                                                "9:15 - 10:00"
                                            ],
                                            "status": False,
                                            "time": "",
                                            "percentage": 0,
                                            "replace": None
                                        }
                                    ]
                                },
                                {
                                    "day": "Четверг",
                                    "date": "8 Августа",
                                    "lessons": [
                                        {
                                            "item": "Русский язык",
                                            "cabinet": "36-2",
                                            "teacher": "Вартабедьян В.Б.",
                                            "event_time": [
                                                "8:30 - 9:15",
                                                "9:15 - 10:00"
                                            ],
                                            "status": False,
                                            "time": "",
                                            "percentage": 0,
                                            "replace": None
                                        }
                                    ]
                                }
                            ]
                        
                    }
                },
            },

            500: {
                "description": "Ошибка при получении расписания",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "Неизвестная ошибка при получении расписания"
                        }
                    }
                },
            },

        }
)
async def get_lessons(
    session: SessionDep, # Сессия базы данных
    group: str = Query(..., description="Группа", example="Исп-232"),
) -> JSONResponse: 
    logger.info(f"Запрос на получения расписания для группы. Группа: {group}")

    cache_schedule: bool | schemas.Schedule_output = await redis.check_lessons(group)

    if cache_schedule:
        logger.debug(f"Расписание есть в кеше redis")

        logger.info(f"Вовзращаем сформированнное json расписание для группы. Группа: {group}")
        return JSONResponse(content=cache_schedule, status_code=200)

    logger.debug(f"Расписание не найдено в кеше redis. Запускем функцию формирования расписания")
    schedule: bool | schemas.Schedule_output = await utils.get_lessons(group, session)

    if schedule:
        logger.debug("Устанавливаем сформированное расписание в кеш redis")
        await redis.set_lesssons(group, schedule)

        logger.debug("Отдаём ответ сформированное расписание")
        return JSONResponse(content=schedule, status_code=200)
    
    else:
        logger.error(f"Ошибка при получении расписания. Отдаём ответ. Группа: {group}")
        return JSONResponse(content={"message": "Неизвестная ошибка при получении расписания"}, status_code=500)
        


@router_lesson.get(
        path="/teacher/{teacher}",
        description="Посмотреть пары для учителя",
)
async def get_lesson_for_teacher(
    session: SessionDep, # Сессия базы данных
    teacher: str = Path(..., description="ФИО учителя", example="Демиденко Наталья Ильинична")
) -> JSONResponse:
    logger.info(f"Запрос на расписание для учителя. Учитель {teacher}")

    getting = await utils.get_lessons_teacher(teacher, session)

    if getting:
        logger.info(f"Отдаём ответ. Список пар учителю")
        return JSONResponse(content=getting, status_code=200)
    
    else:
        logger.error(f"Отдаём ответ произошла ошибка при получении пар учителю")
        return JSONResponse(content={"message": "Неизвестная ошибка при получении пар"}, status_code=500)




@router_lesson.put(
        path="/put",
        description="Установить пару для группы",
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

            500: {
                "description": "Ошибка установки",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "Неизвестная ошибка при установке пары"
                        }
                    }
                },
            },

        }
)
async def put_lesson(
    session: SessionDep, # Сессия базы данных
    payload: schemas.Lesson_input = Body(..., description="Пара для группы в формате JSON",
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

    setting: bool = await utils.put_lesson(payload, session)

    if setting:
        logger.info(f"Отдаём ответ. Пара успешно установлена")
        return JSONResponse(content={'message': "Пара для группы успешно установлена"}, status_code=200)
    
    else:
        logger.error(f"Пара для группы не была установлена. Отдаём ответ")
        return JSONResponse(content={"message": "Неизвестная ошибка при установке пары"}, status_code=500)




@router_lesson.delete(
        path="/remove",
        description="Удалить пару",
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

            500: {
                "description": "Ошибка удаления",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "Неизвестная ошибка при удалении пары"
                        }
                    }
                },
            },

        }
)
async def remove_lesson(
    session: SessionDep, # Сессия базы данных
    payload: schemas.Remove_lesson = Body(..., description="Параметры для удаления пары",
    example={
        "group": "Исп-232",
        "day": "Понедельник",
        "num_lesson": 0,
        "week": 0
    })
) -> JSONResponse: 
    logger.info(f"Запрос на удаление пары. Payload: {payload.model_dump_json()}")

    removing: bool = await utils.remove_lesson(payload, session)

    if removing:
        return JSONResponse(content={'message': "Пара успешно удалена"}, status_code=200)
    
    else:
        logger.error(f"Отдаём ответ ошибка при удалении")
        return JSONResponse(content={"message": "Неизвестная ошибка при удалении пары"}, status_code=500)
