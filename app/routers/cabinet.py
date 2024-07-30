import json
from typing import Optional
from fastapi import APIRouter, Depends, Query, Body, Header, Path
from fastapi.responses import JSONResponse
from ..core import dependencies, config
from ..services import redis, rabbitmq
from .. import models, utils
from loguru import logger
import asyncio

router = APIRouter()


@router.get(
        path="/cabinets",
        tags=["Кабинеты"],
        dependencies=[Depends(dependencies.oauth2_scheme)],
        description="Список всех кабинетов",
)
async def get_cabients() -> JSONResponse:
    logger.info(f"came request list all cabinets")

    getting = await utils.all_cabinets()

    if getting:
        return JSONResponse(content=getting, status_code=200)
    else:
        logger.error("ERROR getting all cabients")
        return JSONResponse(content={"message": "Неизвестная ошибка при получении списка кабинетов"}, status_code=500)
    

@router.put(
        path="/put/cabinet",
        tags=["Кабинеты"],
        dependencies=[Depends(dependencies.oauth2_scheme)],
        description="Добавить кабинет",
)
async def put_cabinet(
    cabinet: models.Cabinet_input
) -> JSONResponse:
    logger.info(f"came request put cabinet {cabinet.cabinet}")

    adding = await utils.put_cabinet(cabinet.cabinet)

    if adding:
        return JSONResponse(content={"message": "Кабинет успешно добавлен"}, status_code=200)
    else:
        logger.error("ERROR add cabinet")
        return JSONResponse(content={"message": "Неизвестная ошибка добавлении кабинета"}, status_code=500)
    



@router.delete(
        path="/remove/cabinet",
        tags=["Кабинеты"],
        dependencies=[Depends(dependencies.oauth2_scheme)],
        description="Удалить кабинет",
)
async def remove_cabinet(
    cabinet: models.Cabinet_input
) -> JSONResponse:
    logger.info(f"came request remove cabinet {cabinet.cabinet}")

    removing = await utils.remove_cabinet(cabinet.cabinet)

    if removing == "not found":
        return JSONResponse(content={"message": "Кабинет не найден"}, status_code=200)
    elif removing:
        return JSONResponse(content={"message": "Кабинет успешно удалён"}, status_code=200)
    else:
        logger.error("ERROR remove cabinet")
        return JSONResponse(content={"message": "Неизвестная ошибка удалении кабинета"}, status_code=500)
    
