import json
from typing import Optional
from fastapi import APIRouter, Depends, Query, Body
from fastapi.responses import JSONResponse
from ..core import dependencies, config
from ..services import redis
from .. import schemas, utils
from loguru import logger
import asyncio

router = APIRouter()


@router.get(
        path="/teachers",
        tags=["Учителя"],
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
        path="/put/teacher",
        tags=["Учителя"],
        description="Добавить учителя",
)
async def put_teacher(
    full_name: schemas.Teacher_input = Body(..., description="ФИО учителя", example={
        "full_name": "Демиденко Наталья Ильинична"
    })
) -> JSONResponse:
    logger.info(f"came request put teacher {full_name.full_name}")

    adding = await utils.put_teacher(full_name.full_name)

    if adding:
        return JSONResponse(content={"message": "Учитель успешно добавлен"}, status_code=200)
    else:
        logger.error("ERROR add teacher")
        return JSONResponse(content={"message": "Неизвестная ошибка добавлении учителей"}, status_code=500)
    




@router.delete(
        path="/remove/teacher",
        tags=["Учителя"],
        description="Удалить учителя",
)
async def remove_teacher(
     full_name: schemas.Teacher_input = Body(..., description="ФИО учителя", example={
        "full_name": "Демиденко Наталья Ильинична"
    })
) -> JSONResponse:
    logger.info(f"came request remove teacher {full_name.full_name}")

    removing = await utils.remove_teacher(full_name.full_name)

    if removing == "not found":
        return JSONResponse(content={"message": "Учитель с таким ФИО не найден"}, status_code=200)
    elif removing:
        return JSONResponse(content={"message": "Учитель успешно удалён"}, status_code=200)
    else:
        logger.error("ERROR add teacher")
        return JSONResponse(content={"message": "Неизвестная ошибка удалении учителей"}, status_code=500)