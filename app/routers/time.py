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
from app.core.dependencies import SessionDep

router_time = APIRouter(prefix="/time", tags=["Время"])

@router_time.get(
        path="",
        summary="Посмотреть время на день и/или пару",
        response_model=schemas.Check_time
)
async def get_time(
        session: SessionDep,
        day: Optional[schemas.Days | None] = Query(None, description="НЕОБЯЗАТЕЛЬНО День недели", example="Понедельник"),
        num_lesson: Optional[int | None] = Query(None, description="НЕОБЯЗАТЕЛЬНО Номер пары, 0-4, где 0 это классный час", ge=0, le=4, example=2),
) -> JSONResponse: 
    logger.info(f"Запрос на получение времени day: {day} num_lesson {num_lesson}")

    getting = await utils.get_time(day=day, num_lesson=num_lesson, session=session)

    if getting == []:
        return JSONResponse(content={"message": "Время еще не было установлено"}, status_code=404)
    if getting:
        return JSONResponse(content=getting.model_dump(), status_code=200)
    else:
        return JSONResponse(content={"message": "Неизвестная ошибка при получении времени"}, status_code=500)
    

@router_time.get(
        path="/weekday",
        summary="Посмотреть текущую неделю и день",
        response_model=schemas.Week_Day
)
async def get_week() -> JSONResponse: 
    logger.info(f"Запрос на получение текущей недели")

    num_day, num_week = await utils.get_day_and_week_number()

    model = schemas.Week_Day(day=schemas.Num_to_day[num_day], week=num_week)
    
    return JSONResponse(content=model.model_dump(), status_code=200)
    


@router_time.post(
        path="",
        summary="Установить или изменить время для пары",
        response_model=schemas.Put_time_out,
        description="Устанавливает или изменяет время для пары и возвращает айди"
)
async def set_time(
        session: SessionDep,
        payload: schemas.Put_time = Body(..., description="Параметры для пары", example={
            "day": "Понедельник",
            "num_lesson": 1,
            "time": "8:30 - 9:15, 9:15 - 10:00"
        })
) -> JSONResponse: 
    logger.info(f"Запрос на установку времени для пары. Payload {payload.model_dump_json()}")

    setting: schemas.Put_time_out | bool = await utils.set_time(payload, session)

    if setting:
        logger.info("Отдаём ответ. Время успешно установлено")
        return JSONResponse(content=setting, status_code=200)
    else:
        logger.error("Отдаём ответ. Неизвестная ошибка")
        return JSONResponse(content={"message": "Неизвестная ошибка при установке времени"}, status_code=500)


@router_time.delete(
        path="",
        summary="Удалить время",
        responses={
            200: {
                "description": "Время удалено",
                "content": {
                    "application/json": {
                        "example": 
                       {
                           "message": "Время успешно удалено"
                       }
                    }
                },
            },
            404: {
                "description": "Не найдено",
                "content": {
                    "application/json": {
                        "example": 
                       {
                           "message": "Удаляемое время не найдено"
                       }
                    }
                },
            },

            500: {
                "description": "Ошибка при удалении",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "Неизвестная ошибка при удалении времени"
                        }
                    }
                },
            },
        }
)
async def remove_time(
        session: SessionDep,
        payload: schemas.Remove_time = Body(..., description="Параметры времени", example={
            "day": "Понедельник",
            "num_lesson": 1
        })
) -> JSONResponse: 
    logger.info(f"Запрос на удаление времени. Payload: {payload.model_dump_json()}")

    removing: bool | str = await utils.remove_time(payload, session)

    if removing == "not found":
        logger.info(f"Отдаём ответ время в бд не найдено")
        return JSONResponse(content={"message": "Удаляемое время не найдено"}, status_code=404)
    
    elif removing:        
        logger.info(f"Отдаём ответ время было удалено")
        return JSONResponse(content={"message": "Время успешно удалено"}, status_code=200)
    
    else:
        logger.info(f"Отдаём ответ неизвестная ошибка при удалении времени")
        return JSONResponse(content={"message": "Неизвестная ошибка при удалении времени"}, status_code=500)
    



