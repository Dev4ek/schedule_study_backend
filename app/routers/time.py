import json
from fastapi import APIRouter, Depends, Query, Body
from fastapi.responses import JSONResponse
from ..core import dependencies, config
from ..services import redis, rabbitmq, lesson_manage
from loguru import logger
import asyncio
from .. import models

router = APIRouter()

@router.post("/set/time", tags=["Время"])
async def set_time(
    token: str = Depends(dependencies.oauth2_scheme), # token authentication
    day: str = Query(..., description="День недели, например, Понедельник, Вторник..."),
    num_lesson: int = Query(..., description="Номер пары, 0-4, где 0 это классный час", ge=0, le=4),
    time: str = Body(..., description="Время для пары")
    ) -> JSONResponse: 
    
    num_day = models.Day_num[day]


    setting = await lesson_manage.time_utils.set_time(num_day=num_day, num_lesson=num_lesson, time=time)

    if setting:
        return JSONResponse(content={"message": "Время успешно установлено"}, status_code=200)
    else:
        return JSONResponse(content={"message": "Неизвестная ошибка при установке времени"}, status_code=500)