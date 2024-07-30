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
        tags=["Группы"],
        dependencies=[Depends(dependencies.oauth2_scheme)],
        description="Список всех групп",
)
async def get_teachers() -> JSONResponse:
    logger.info("came request list all groups")

    getting = await utils.all_groups()

    if getting:
        return JSONResponse(content=getting, status_code=200)
    else:
        logger.error("ERROR getting all groups")
        return JSONResponse(content={"message": "Неизвестная ошибка при получении списка групп"}, status_code=500)
    



@router.put(
        path="/put/group",
        tags=["Группы"],
        dependencies=[Depends(dependencies.oauth2_scheme)],
        description="Добавить группу",
)
async def put_group(
    group: models.Group_input = Body(..., description="Группа")
) -> JSONResponse:
    logger.info(f"came request add group {group.group}")

    adding = await utils.put_group(group.group)

    if adding:
        return JSONResponse(content={"message": "Группа успешно добавлена"}, status_code=200)
    else:
        logger.error("ERROR add group")
        return JSONResponse(content={"message": "Неизвестная ошибка добавлении группы"}, status_code=500)
    


@router.delete(
        path="/remove/group",
        tags=["Группы"],
        dependencies=[Depends(dependencies.oauth2_scheme)],
        description="Удалить группу",
)
async def remove_group(
    group: models.Group_input
) -> JSONResponse:
    logger.info(f"came request remove group {group.group}")

    removing = await utils.remove_group(group.group)

    if removing == "not found":
        return JSONResponse(content={"message": "Группа не найдена"}, status_code=200)
    elif removing:
        return JSONResponse(content={"message": "Группа успешно удалена"}, status_code=200)
    else:
        logger.error("ERROR remove group")
        return JSONResponse(content={"message": "Неизвестная ошибка удалении группы"}, status_code=500)
    
