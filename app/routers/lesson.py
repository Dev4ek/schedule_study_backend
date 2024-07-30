import json
from typing import Optional
from fastapi import APIRouter, Depends, Query, Body
from fastapi.responses import JSONResponse
from ..core import dependencies, config
from ..services import redis, rabbitmq
from .. import models, utils
from loguru import logger
import asyncio


router = APIRouter()



@router.get(
        path="/app/lessons", 
        tags=["Расписание"],
        dependencies=[
            Depends(dependencies.oauth2_scheme),
            Depends(dependencies.verify_version)
            ],
        description="Посмотреть все пары для группы (ДЛЯ ПРИЛОЖЕНИЯ)",
        response_model=models.Schedule_output,
)
async def get_lessons(
    group: str = Query(..., description="Группа", example="Исп-232"),
) -> JSONResponse: 

    logger.info(f"Сame request GET schedule: {group}")

    # get cache redis
    cache_schedule = await redis.check_schedule(group)

    # if schedule in cache, return it
    if cache_schedule:
        logger.debug(f"schedule exists in cache redis: {group}")

        # str to json schedule
        schedule = json.loads(cache_schedule)

        return JSONResponse(content=schedule, status_code=200)


    # send request processing to rabbitmq
    schedule_str = await rabbitmq.send_in_queue_schedule(group)

    if schedule_str:
        logger.info(f"response schedule on group: {group}")

        # str to json schedule
        schedule = json.loads(schedule_str)

        # save schedule in cache redis
        await redis.set_schedule(group, schedule_str)

        # return schedule
        return JSONResponse(content=schedule, status_code=200)
    
    else:
        logger.critical(f"CRITICAL ENDPOINT get lessons : {group}")
        return JSONResponse(content={"message": "Неизвестная ошибка при получении расписания"}, status_code=500)
        


@router.put(
        path="/put/lesson",
        tags=["Расписание"],
        dependencies=[Depends(dependencies.oauth2_scheme)],
        description="Установить пару для группы",
)
async def set_lesson(
    lesson: models.Lesson_input = Body(..., description="Пара для группы в формате JSON",
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





@router.delete(
        path="/remove/lesson",
        tags=["Расписание"],
        dependencies=[Depends(dependencies.oauth2_scheme)],
        description="Удалить пару",
)
async def remove_lesson(
    lesson: models.Remove_lesson = Body(..., description="Параметры для пары",
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
