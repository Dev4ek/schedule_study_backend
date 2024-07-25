import json
from typing import Optional
from fastapi import APIRouter, Depends, Query, Body
from fastapi.responses import JSONResponse
from ..core import dependencies, config
from ..services import redis, rabbitmq, lesson_manage
from .. import models
from loguru import logger
import asyncio


router = APIRouter()


@router.post(
        path="/set/lesson",
        tags=["Расписание"],
        dependencies=[Depends(dependencies.oauth2_scheme)],
        description="Установить в расписании пару",
)
async def set_lesson(
    lesson: models.Lesson_input = Body(..., description="Пара для группы в формате JSON"),
) -> JSONResponse: 

    logger.info(f"set lesson for group: {lesson.group}")


    setting = await lesson_manage.lesson_utils.set_lesson(
                                                            lesson=lesson,
                                                            )

    if setting:
        logger.info(f"schedule set for group: {lesson.group}")

        return JSONResponse(content={'message': "Расписание для группы было установлено"}, status_code=200)
    
    else:
        logger.critical(f"schedule not set for group: {lesson.group}")
        return JSONResponse(content={"message": "Неизвестная ошибка при установке расписания"}, status_code=500)


@router.get(
        path="/lessons", 
        tags=["Расписание"],
        dependencies=[
            Depends(dependencies.oauth2_scheme),
            Depends(dependencies.verify_version)
            ],
        description="Посмотреть всё расписание для группы"
)
async def get_lessons(
    group: str = Query(..., description="Название группы, например, Исп-232")
    ) -> JSONResponse: 

    logger.info(f"came request GET schedule: {group}")

    # get cache redis
    cache_schedule = await redis.check_schedule(group)

    # if schedule in cache, return it
    if cache_schedule:
        logger.debug(f"schedule exists in cache redis: {group}")

        # str to json schedule
        schedule = json.loads(cache_schedule)

        # processing time now in schedule
        schedule_time = await lesson_manage.time_utils.timing_couples(schedule)


        return JSONResponse(content=schedule_time, status_code=200)


    # send request processing to rabbitmq
    schedule_str = await rabbitmq.send_in_queue_schedule(group)

    if schedule_str:
        logger.info(f"response schedule on group: {group}")

        # str to json schedule
        schedule = json.loads(schedule_str)

        # save schedule in cache redis
        # await redis.set_schedule(group, schedule_time)

        # return schedule
        return JSONResponse(content=schedule, status_code=200)
    
    else:
        logger.critical(f"schedule not exists for group: {group}")
        return JSONResponse(content={"message": "Неизвестная ошибка при получении расписания"}, status_code=500)
        
