import json
from typing import Optional
from fastapi import APIRouter, Depends, Query, Body
from fastapi.responses import JSONResponse
from ..core import dependencies, config
from ..services import redis
from loguru import logger
import asyncio
from .. import schemas, utils
from icecream import ic

router = APIRouter()


@router.get(
        path="/time",
        tags=["Время"],
        description="Посмотреть время на день / на пару",
)
async def get_time(
        day: Optional[str | None] = Query(None, description="День недели", example="Понедельник"),
        num_lesson: Optional[int | None] = Query(None, description="Номер пары, 0-4, где 0 это классный час", ge=0, le=4, example=2),
    ) -> JSONResponse: 
    logger.info("Came request to get time")

    getting = await utils.get_time(day=day, num_lesson=num_lesson)

    if getting == []:
        return JSONResponse(content={"message": "Время еще не было установлено"}, status_code=200)
    if getting:
        return JSONResponse(content=getting, status_code=200)
    else:
        return JSONResponse(content={"message": "Неизвестная ошибка при получении времени"}, status_code=500)
    


@router.put(
        path="/put/time",
        tags=["Время"],
        description="Установить время для пары",
)
async def put_time(
        payload: schemas.Put_time = Body(..., description="json data for time", example={
            "day": "Понедельник",
            "num_lesson": 1,
            "time": "8:30 - 9:15, 9:15 - 10:00"
        })
    ) -> JSONResponse: 
    logger.info(f"Came request to set time {payload.day} {payload.num_lesson}, {payload.time}")

    num_day = schemas.Day_num[payload.day]

    setting = await utils.set_time(num_day=num_day, num_lesson=payload.num_lesson, time=payload.time)

    if setting:
        return JSONResponse(content={"message": "Время успешно установлено"}, status_code=200)
    else:
        return JSONResponse(content={"message": "Неизвестная ошибка при установке времени"}, status_code=500)



@router.delete(
        path="/remove/time",
        tags=["Время"],
        description="Удалить установеленное время"
)
async def remove_time(
        payload: schemas.Remove_time = Body(..., description="Удаление времени", example={
            "day": "Понедельник",
            "num_lesson": 1
        })
) -> JSONResponse: 

    logger.info(f"Came request to remove time {payload.day}, {payload.num_lesson}")
    
    num_day = schemas.Day_num[payload.day]

    removing = await utils.remove_time(num_day=num_day, num_lesson=payload.num_lesson)

    if removing == "not found":
        return JSONResponse(content={"message": "Время на такой день и пару не найдено"}, status_code=200)
    elif removing:        
        return JSONResponse(content={"message": "Время было удалено"}, status_code=200)
    else:
        return JSONResponse(content={"message": "Неизвестная ошибка при удалении времени"}, status_code=500)
    



