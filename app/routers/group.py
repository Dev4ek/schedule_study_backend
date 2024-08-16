from fastapi import APIRouter, Path
from fastapi.responses import JSONResponse

from app import schemas
from .. import utils
from loguru import logger
from app.core.dependencies import SessionDep
from app.services import database as db

router_group = APIRouter(prefix="/group", tags=["Группы"])

@router_group.get(
        path="/all",
        summary="Список всех групп",
        response_model=list[schemas.info_group]
)
async def get_groups(
    session: SessionDep # Сессия базы даныых
) -> JSONResponse:
    logger.info("Запрос на получение списка всех групп")

    logger.debug("Выполняем запрос в дб")
    result = await session.execute(
            db.select(db.table.Groups.id, db.table.Groups.group)
            .order_by(db.table.Groups.group)
    )

    groups_data = result.all()

    logger.debug("Формируем pydantic model для ответа")
    groups = []
    for group in groups_data:
        groups.append(
            schemas.info_group(
            group_id = group.id,
            group = group.group
            ).model_dump())

    return JSONResponse(content=groups, status_code=200)
    

@router_group.put(
        path="/{group}",
        summary="Добавить группу",
        response_model=schemas.group_id
)
async def put_group(
    session: SessionDep, # Сессия базы даных
    group: str = Path(..., title="Группа", example="Исп-232")
) -> JSONResponse:
    logger.info(f"Запрос на вставку группы. Группа: {group}")

    adding: bool | str | schemas.group_id = await utils.put_group(group, session)

    if adding == "exists":
        logger.info("Группа уже существует. Отдаём ответ")
        return JSONResponse(content={"message": "Группа уже существует"}, status_code=409)

    elif adding:
        logger.info("Группа успешно добавлена. Отдаём ответ")
        return JSONResponse(content=adding.model_dump(), status_code=200)

    else:
        logger.error("Неизвестная ошибка при добавлении группы. Отдаём ответ")
        return JSONResponse(content={"message": "Неизвестная ошибка при добавлении группы"}, status_code=500)


@router_group.delete(
        path="/{group}",
        summary="Удалить группу",
        responses={
            200: {
                "description": "Успешное удаление",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "Группа успешно удалена"
                        }
                    }
                },
            },

            404: {
                "description": "Не найдена",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "Группа не найдена"
                        }
                    }
                },
            },

            500: {
                "description": "Ошибка при удалении группы",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "Неизвестная ошибка удалении группы"
                        }
                    }
                },
            },
        },
)
async def remove_group(
    session: SessionDep, # Сессия базы даных
    group: str = Path(..., description="Группа", example="Исп-232")
) -> JSONResponse:
    logger.info(f"Запрос на удаление группы. Группа: {group}")

    removing: bool | str = await utils.remove_group(group, session)

    if removing == "not found":
        logger.info("Группа не найдена. Отдаём ответ")
        return JSONResponse(content={"message": "Группа не найдена"}, status_code=404)
    
    elif removing:
        logger.info("Группа успешно удалена. Отдаём ответ")
        return JSONResponse(content={"message": "Группа успешно удалена"}, status_code=200)
    
    else:
        logger.error("Ошибка при удалении группы. Отдаём ответ")
        return JSONResponse(content={"message": "Неизвестная ошибка удалении группы"}, status_code=500)
    
