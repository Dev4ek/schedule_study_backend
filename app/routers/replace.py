import json
from typing import Optional
from fastapi import APIRouter, Depends, Query, Body,  Path
from fastapi.responses import JSONResponse
from ..core import dependencies, config
from ..services import redis, rabbitmq
from .. import models, utils
from loguru import logger
import asyncio

router = APIRouter()

@router.get(
        path="/replacements",
        tags=["Замены"],
        dependencies=[Depends(dependencies.oauth2_scheme)],
        description="Список всех замен",
)
async def get_replacements(
    group: str = Query(..., description="Группа", example="Исп-232")
) -> JSONResponse:
    logger.info("came request list all groups")

    getting = await utils.all_replacemetns(group)

    if getting:
        return JSONResponse(content=getting, status_code=200)
    else:
        logger.error("ERROR getting all groups")
        return JSONResponse(content={"message": "Неизвестная ошибка при получении списка групп"}, status_code=500)


@router.put(
        path="/put/replace",
        tags=["Замены"],
        dependencies=[Depends(dependencies.oauth2_scheme)],
        description="Добавить замену",
)
async def put_replace(
    replace: models.Replace_input = Body(..., description="Замена", example={
        "group": "Исп-232",
        "date": "23 Сентября",
        "day": "Понедельник",
        "item": "Русский язык",
        "num_lesson": 1,
        "teacher": "Вартабедьян Виктория Борисовна",
        "cabinet": "36-2"
    })
) -> JSONResponse:
    
    logger.info(f"came request add replace {replace}")

    adding = await utils.put_replace(replace)

    if adding == "not date":
        return JSONResponse(content={"message": "Чтобы добавить замены с другой датой, удалите все передыдущие замены"}, status_code=200)

    elif adding:
        return JSONResponse(content={"message": "Замена успешно добавлена"}, status_code=200)
    else:
        logger.error("ERROR add replace")
        return JSONResponse(content={"message": "Неизвестная ошибка при добавлении замены"}, status_code=500)


@router.delete(
        path="/remove/replace",
        tags=["Замены"],
        dependencies=[Depends(dependencies.oauth2_scheme)],
        description="Удалить замену",
)
async def remove_replace(
    replace: models.Replace_remove = Body(..., description="Удалить замену", example={
        "group": "Исп-232",
        "day": "Понедельник",
        "num_lesson": 1,
    })
) -> JSONResponse:
    logger.info(f"came request remove replace {replace}")

    removing = await utils.remove_replace(replace)

    if removing == "not found":
        return JSONResponse(content={"message": "Замена не найдена"}, status_code=200)
    elif removing:
        return JSONResponse(content={"message": "Замена успешно удалена"}, status_code=200)
    else:
        logger.error("ERROR remove replace")
        return JSONResponse(content={"message": "Неизвестная ошибка удалении замены"}, status_code=500)
