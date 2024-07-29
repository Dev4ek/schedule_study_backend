import json
from typing import Optional
from fastapi import APIRouter, Depends, Query, Body
from fastapi.responses import JSONResponse
from ..core import dependencies, config
from ..services import redis, rabbitmq
from .. import models, utils
from loguru import logger
import asyncio

router = APIRouter()


@router.get(
        path="/teachers",
        tags=["Учителя"],
        dependencies=[Depends(dependencies.oauth2_scheme)],
        description="Список всех учителей",
)
async def get_teachers() -> JSONResponse:
    logger.info("came request list all teachers")

    getting = await utils.all_teachers()

    if getting:
        return JSONResponse(content=getting, status_code=200)
    else:
        logger.error("ERROR getting all teachers")
        return JSONResponse(content={"message": "Неизвестная ошибка при получении списка учителей"}, status_code=500)
    



@router.put(
        path="/set/teacher",
        tags=["Учителя"],
        dependencies=[Depends(dependencies.oauth2_scheme)],
        description="Добавить учителя",
)
async def set_teacher(
    full_name: str = Body(..., description="ФИО", example="Демиденко Наталья Ильинична")
) -> JSONResponse:
    logger.info("came request add teacher")

    adding = await utils.set_teacher(full_name)

    if adding:
        return JSONResponse(content={"message": "Учитель успешно добавлен"}, status_code=200)
    else:
        logger.error("ERROR add teacher")
        return JSONResponse(content={"message": "Неизвестная ошибка добавлении учителей"}, status_code=500)
    




@router.delete(
        path="/remove/teacher",
        tags=["Учителя"],
        dependencies=[Depends(dependencies.oauth2_scheme)],
        description="Удалить учителя",
)
async def remove_teacher(
    full_name: str = Query(..., description="ФИО учителя", example="Демиденко Наталья Ильинична")
) -> JSONResponse:
    logger.info("came request remove teacher")

    removing = await utils.remove_teacher(full_name)

    if removing == "not found":
        return JSONResponse(content={"message": "Учитель с таким ФИО не найден"}, status_code=200)
    elif removing:
        return JSONResponse(content={"message": "Учитель успешно удалён"}, status_code=200)
    else:
        logger.error("ERROR add teacher")
        return JSONResponse(content={"message": "Неизвестная ошибка удалении учителей"}, status_code=500)