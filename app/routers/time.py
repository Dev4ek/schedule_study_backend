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
        path="/",
        description="Посмотреть время на день / на пару",
        responses={
            200: {
                "description": "Список времени",
                "content": {
                    "application/json": {
                        "example": 
                        [
                            {
                                "day": "Понедельник",
                                "time": [
                                    {
                                        "num_lesson": 0,
                                        "event_time": "8:30 - 9:15, 9:15 - 10:00"
                                    }
                                ]
                            },
                            {
                                "day": "Среда",
                                "time": [
                                    {
                                        "num_lesson": 0,
                                        "event_time": "8:30 - 9:15, 9:15 - 10:00"
                                    },
                                    {
                                        "num_lesson": 1,
                                        "event_time": "10:20 - 11:05, 11:20 - 12:05"
                                    },
                                ]
                                }
                            ]
                    }
                },
            },
            404: {
                "description": "Не найдено",
                "content": {
                    "application/json": {
                        "example": 
                        {
                            "message": "Время еще не было установлено"
                        }
                          
                    }
                },
            },

            500: {
                "description": "Ошибка",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "Неизвестная ошибка при получении времени"
                        }
                    }
                },
            },
        }
)
async def get_time(
        session: SessionDep,
        day: Optional[str | None] = Query(None, description="День недели", example="Понедельник"),
        num_lesson: Optional[int | None] = Query(None, description="Номер пары, 0-4, где 0 это классный час", ge=0, le=4, example=2),
) -> JSONResponse: 
    logger.info(f"Запрос на получение времени day: {day} num_lesson {num_lesson}")

    getting = await utils.get_time(day=day, num_lesson=num_lesson, session=session)

    if getting == []:
        return JSONResponse(content={"message": "Время еще не было установлено"}, status_code=404)
    if getting:
        return JSONResponse(content=getting, status_code=200)
    else:
        return JSONResponse(content={"message": "Неизвестная ошибка при получении времени"}, status_code=500)
    


@router_time.put(
        path="/put",
        description="Установить время для пары",
        responses={
            200: {
                "description": "Список времени",
                "content": {
                    "application/json": {
                        "example": 
                       {
                           "message": "Время успешно установлено"
                       }
                    }
                },
            },

            500: {
                "description": "Ошибка при установке",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "Неизвестная ошибка при установке времени"
                        }
                    }
                },
            },
        }
)
async def put_time(
        session: SessionDep,
        payload: schemas.Put_time = Body(..., description="Параметры для пары", example={
            "day": "Понедельник",
            "num_lesson": 1,
            "time": "8:30 - 9:15, 9:15 - 10:00"
        })
) -> JSONResponse: 
    logger.info(f"Запрос на вставку времени. Payload {payload.model_dump_json()}")

    setting: bool = await utils.set_time(payload, session)

    if setting:
        logger.info("Отдаём ответ. Время успешно установлено")
        return JSONResponse(content={"message": "Время успешно установлено"}, status_code=200)
    else:
        logger.error("Отдаём ответ. Неизвестная ошибка")
        return JSONResponse(content={"message": "Неизвестная ошибка при установке времени"}, status_code=500)


@router_time.delete(
        path="/remove",
        description="Удалить установеленное время",
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
    



