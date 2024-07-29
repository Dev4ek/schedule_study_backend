import json
from typing import Optional
from fastapi import APIRouter, Depends, Query, Body
from fastapi.responses import JSONResponse
from ..core import dependencies, config
from ..services import redis, rabbitmq
from loguru import logger
import asyncio
from .. import models, utils
from icecream import ic

router = APIRouter()


@router.get(
        path="/time",
        tags=["Время"],
        description="Посмотреть время на день / на пару",
        dependencies=[Depends(dependencies.oauth2_scheme)]
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
        path="/set/time",
        tags=["Время"],
        description="Установить время для пары",
        dependencies=[Depends(dependencies.oauth2_scheme)]
)
async def set_time(
        day: str = Body(..., description="День недели", example="Понедельник"),
        num_lesson: int = Body(..., description="Номер пары, 0-4, где 0 это классный час", ge=0, le=4, example=2),
        time: str = Body(..., description="Время для пары", example="8:30 - 9:15, 9:15 - 10:00")
    ) -> JSONResponse: 
    logger.info("Came request to set time")

    num_day = models.Day_num[day]

    setting = await utils.set_time(num_day=num_day, num_lesson=num_lesson, time=time)

    if setting:
        return JSONResponse(content={"message": "Время успешно установлено"}, status_code=200)
    else:
        return JSONResponse(content={"message": "Неизвестная ошибка при установке времени"}, status_code=500)
    





@router.delete(
        path="/remove/time",
        tags=["Время"],
        description="Удалить установеленное время",
        dependencies=[Depends(dependencies.oauth2_scheme)]
)
async def remove_time(
        day: str = Body(..., description="День недели", example="Понедельник"),
        num_lesson: int = Body(..., description="Номер пары, 0-4, где 0 это классный час", ge=0, le=4, example=2),
    ) -> JSONResponse: 

    logger.info("Came request to remove time")
    
    num_day = models.Day_num[day]

    removing = await utils.remove_time(num_day=num_day, num_lesson=num_lesson)

    if removing == "not found":
        return JSONResponse(content={"message": "Время на такой день и пару не найдено"}, status_code=200)
    elif removing:        
        return JSONResponse(content={"message": "Время было удалено"}, status_code=200)
    else:
        return JSONResponse(content={"message": "Неизвестная ошибка при удалении времени"}, status_code=500)
    



