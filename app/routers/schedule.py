import json
from fastapi import APIRouter, Depends, Query, Body
from fastapi.responses import JSONResponse
from ..core import dependencies, config
from ..services import redis, rabbitmq, schedule_manage
from loguru import logger
import asyncio

router = APIRouter()

# from asyncio import Semaphore
# sem = Semaphore(config.count_threads)


@router.get("/schedule", tags=["Расписание"])
async def get_schedule(
    token: str = Depends(dependencies.oauth2_scheme), # token authentication
    client_version: str = Depends(dependencies.verify_version), # client version verification

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
        schedule_time = await schedule_manage.time_utils.timing_couples(schedule)


        return JSONResponse(content=schedule_time, status_code=200)


    # send request processing to rabbitmq
    schedule_str = await rabbitmq.send_in_queue_schedule(group)

    if schedule_str:
        logger.info(f"response schedule on group: {group}")

        # str to json schedule
        schedule = json.loads(schedule_str)

        # processing time now in schedule
        schedule_time = await schedule_manage.time_utils.timing_couples(schedule)



        # save schedule in cache redis
        await redis.set_schedule(group, schedule_time)

        # return schedule
        return JSONResponse(content=schedule, status_code=200)
    
    else:
        logger.critical(f"schedule not exists for group: {group}")
        return JSONResponse(content={"message": "Неизвестная ошибка при получении расписания"}, status_code=500)
        



@router.post("/set/schedule", tags=["Расписание"])
async def set_schedule(
    token: str = Depends(dependencies.oauth2_scheme), 
    group: str = Query(..., description="Название группы, например, Исп-232"),
    num_lesson: int = Query(..., description="Номер пары"),
    schedule: list[dict] = Body(..., description="Расписание для группы в формате списка JSON")
    ) -> JSONResponse: 

    logger.info(f"set schedule for group: {group}")

    setting = await schedule_manage.schedule_utils.set_schedule(group=group, schedule=schedule, num_lesson=num_lesson)

    if setting:

        logger.info(f"schedule set for group: {group}")

        return JSONResponse(content={'message': "Расписание для группы было установлено"}, status_code=200)
    
    else:

        logger.critical(f"schedule not set for group: {group}")
        return JSONResponse(content={"message": "Неизвестная ошибка при установке расписания"}, status_code=500)

