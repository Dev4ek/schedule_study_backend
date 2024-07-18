import time
from typing import Annotated
from fastapi import APIRouter, Depends, Header, Query
from fastapi.responses import JSONResponse
from ..core import dependencies
from ..services import redis, rabbitmq
from icecream import ic
import asyncio
from loguru import logger

router = APIRouter()


@router.get("/schedule", tags=["Расписание"])
async def get_schedule(
    token: str = Depends(dependencies.oauth2_scheme), 
    client_version: str = Depends(dependencies.verify_version), 
    group: str = Query(..., description="Название группы, например, Исп-232")
    ) -> JSONResponse: 



    time.sleep(0.6)
    return JSONResponse(status_code=200, content=[
                {
                    "day": "Понедельник (Сегодня)",
                    "date": "27 Сентября",
                    "schedule":
                    [{
                        "title": "ОБЖ Лизенко (312-1)",
                        "event_time": ["8:30 - 10:00"],
                        "active": True,
                        "time": "До конца 32 минуты"
                    },
                    {
                        "title": "Математика Синицина (5а-2)",
                        "event_time": ["10:20 - 11:00", "11:10 - 12:05"],
                        "active": False,
                        "time_left": 0,
                    },
                    {
                        "title": "Литература Вартабедьян (32-2)",
                        "event_time": ["12:30 - 13:15", "13:35 - 14:20"],
                        "active": False,
                        "time_left": 0,
                    },
                    ]
                },
                 {
                    "day": "Вторник",
                    "date": "28 Сентября",
                    "schedule":
                    [{
                        "title": "СИСС Киреева (411-1)",
                        "event_time": [""],
                        "active": False,
                        "time": "До конца 32 минуты"
                    },
                    {
                        "title": "Английский Колот (31-2)",
                        "event_time": ["", ""],
                        "active": False,
                        "time_left": 0,
                    },
                    {
                        "title": "Физкудьтура Калогривый",
                        "event_time": ["", ""],
                        "active": False,
                        "time_left": 0,
                    },
                    ]
                },
                                 {
                    "day": "Среда",
                    "date": "29 Сентября",
                    "schedule":
                    [{
                        "title": "СИСС Киреева (411-1)",
                        "event_time": [""],
                        "active": False,
                        "time": "До конца 32 минуты"
                    },
                    {
                        "title": "Английский Колот (31-2)",
                        "event_time": ["", ""],
                        "active": False,
                        "time_left": 0,
                    },
                    {
                        "title": "Физкультура Калогривый",
                        "event_time": ["", ""],
                        "active": False,
                        "time_left": 0,
                    },
                    ]
                },
                                 {
                    "day": "Четверг",
                    "date": "30 Сентября",
                    "schedule":
                    [{
                        "title": "СИСС Киреева (411-1)",
                        "event_time": [""],
                        "active": False,
                        "time": "До конца 32 минуты"
                    },
                    {
                        "title": "Английский Колот (31-2)",
                        "event_time": [""],
                        "active": False,
                        "time_left": 0,
                    },
                    {
                        "title": "Физкудьтура Калогривый",
                        "event_time": [""],
                        "active": False,
                        "time_left": 0,
                    },
                    ]
                },
            ]
    )


    logger.info(f"came request GET schedule: {group}")

    try:        
        # get cache redis
        cache_schedule = await redis.check_schedule(group)

        # if schedule in cache, return it
        if cache_schedule:
            logger.debug(f"schedule exists in cache redis: {group}")

            return JSONResponse(content=cache_schedule, status_code=200)

        # send request to rabbitmq
        schedule = await rabbitmq.send_in_queue(group)

        if schedule:
            #set schedule in cache redis
            await redis.set_schedule(group, schedule)

            logger.info(f"response schedule on group: {group}")
            # return schedule
            return {'ok': schedule}
        
        else:
            logger.critical(f"schedule not exists for group: {group}")
            return JSONResponse(status_code=500, content={"message": "Неизвестная ошибка при получении расписания"})
    
    except Exception as e:
        logger.exception(f"CRITICAL ERRPR GET schedule: {group}")
        return JSONResponse(status_code=500, content={"message": "Неизвестная ошибка при получении расписания"})