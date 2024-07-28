import json
from typing import Optional
from fastapi import APIRouter, Depends, Query, Body
from fastapi.responses import JSONResponse
from ..core import dependencies, config
from ..services import redis, rabbitmq, utils
from loguru import logger
import asyncio
from .. import models
from icecream import ic

router = APIRouter()

@router.post(
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
    
    num_day = models.Day_num[day]

    setting = await utils.time_utils.set_time(num_day=num_day, num_lesson=num_lesson, time=time)

    if setting:
        return JSONResponse(content={"message": "Время успешно установлено"}, status_code=200)
    else:
        return JSONResponse(content={"message": "Неизвестная ошибка при установке времени"}, status_code=500)
    



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
    
    getting = await utils.time_utils.get_time(day=day, num_lesson=num_lesson)

    if getting:
        return JSONResponse(content=getting, status_code=200)
    else:
        return JSONResponse(content={"message": "Неизвестная ошибка при получении времени"}, status_code=500)
    

