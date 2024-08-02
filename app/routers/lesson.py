import json
from typing import Optional
from fastapi import APIRouter, Depends, Query, Body
from fastapi.responses import JSONResponse
from ..core import dependencies, config
from ..services import redis
from .. import schemas, utils
from loguru import logger
from app.core.dependencies import SessionDep
import asyncio


router_lesson = APIRouter(prefix="/lesson", tags=["Расписание"])


@router_lesson.get(
        path="/app", 
        dependencies=[Depends(dependencies.verify_version)],
        description="Посмотреть все пары для группы (ДЛЯ ПРИЛОЖЕНИЯ)",
        response_model=schemas.Schedule_output,
)
async def get_lessons(
    session: SessionDep,
    group: str = Query(..., description="Группа", example="Исп-232"),
) -> JSONResponse: 
    logger.info(f"Запрос на получения расписания для группы. Группа: {group}")

    cache_schedule = await redis.check_lessons(group)

    if cache_schedule:
        logger.debug(f"Расписание есть в кеше redis")

        logger.info(f"Вовзращаем сформированнное json расписание для группы. Группа: {group}")
        return JSONResponse(content=cache_schedule, status_code=200)

    logger.debug(f"Расписание не найдено в кеше redis. Запускем функцию формирования расписания")
    schedule = await utils.get_lessons(group, session)

    if schedule:
        logger.debug("Устанавливаем сформированное расписание в кеш redis")
        await redis.set_lesssons(group, schedule)

        logger.debug("Отдаём ответ сформированное расписание")
        return JSONResponse(content=schedule, status_code=200)
    
    else:
        logger.critical(f"CRITICAL ENDPOINT get lessons : {group}")
        return JSONResponse(content={"message": "Неизвестная ошибка при получении расписания"}, status_code=500)
        


@router_lesson.put(
        path="/put/lesson",
        tags=["Расписание"],
        description="Установить пару для группы",
)
async def set_lesson(
    lesson: schemas.Lesson_input = Body(..., description="Пара для группы в формате JSON",
    example={
        "group": "Исп-232",
        "day": "Понедельник",
        "item": "Классный час",
        "num_lesson": 2,
        "teacher": "Демиденко Наталья Ильинична",
        "cabinet": "405-1",
        "week": 0
    }
),
) -> JSONResponse: 

    logger.info(f"set lesson for group: {lesson.group}")

    setting = await utils.lesson_utils.set_lesson(lesson=lesson,)

    if setting:
        logger.info(f"schedule set for group: {lesson.group}")

        return JSONResponse(content={'message': "Расписание для группы было установлено"}, status_code=200)
    
    else:
        logger.critical(f"schedule not set for group: {lesson.group}")
        return JSONResponse(content={"message": "Неизвестная ошибка при установке расписания"}, status_code=500)





@router_lesson.delete(
        path="/remove/lesson",
        tags=["Расписание"],
        description="Удалить пару",
)
async def remove_lesson(
    lesson: schemas.Remove_lesson = Body(..., description="Параметры для пары",
    example={
        "group": "Исп-232",
        "day": "Понедельник",
        "num_lesson": 0,
        "week": 0
    })
) -> JSONResponse: 

    logger.info(f"remove lesson for group: {lesson.group} day: {lesson.day}, num_lesson: {lesson.num_lesson}, week: {lesson.week}")

    removing = await utils.remove_lesson(lesson.group, lesson.day, lesson.num_lesson, lesson.week)

    if removing:
        return JSONResponse(content={'message': "Успешно удалено"}, status_code=200)
    
    else:
        logger.critical(f"error removing lesson")
        return JSONResponse(content={"message": "Неизвестная ошибка при удалении пары"}, status_code=500)
