from fastapi import APIRouter, Path
from fastapi.responses import JSONResponse
from .. import utils
from loguru import logger
from app.core.dependencies import SessionDep


router_cabinet = APIRouter(prefix="/cabinet", tags=["Кабинеты"])


@router_cabinet.get(
        path="/all",
        description="Список всех кабинетов",
        responses={
            200: {
                "description": "Получен список",
                "content": {
                    "application/json": {
                        "example": [
                            {
                                "id": 1,
                                "cabinet": "405-1"
                            },
                            {
                                "id": 2,
                                "cabinet": "36-2"
                            }
                            ]
                    }
                },
            },

            500: {
                "description": "Ошибка при получении списка",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "Неизвестная ошибка при получении списка кабинетов"
                        }
                    }
                },
            },

        }
)
async def get_cabients(
    session: SessionDep # Сессия базы данных
) -> JSONResponse:
    logger.info(f"Запрос на получение всех кабинетов")

    getting: dict | bool = await utils.all_cabinets(session)

    if getting:
        logger.info("Отправляем ответ список кабинетов")
        return JSONResponse(content=getting, status_code=200)
    else:
        logger.error("Произошла ошибка на получения списка")
        return JSONResponse(content={"message": "Неизвестная ошибка при получении списка кабинетов"}, status_code=500)
    

@router_cabinet.put(
        path="/put/{cabinet}",
        description="Добавить кабинет",
        responses={
            200: {
                "description": "Успешное добавление",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "Кабинет успешно добавлен"
                        }
                    }
                },
            },

            409: {
                "description": "Ошибка при добавлении",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "Кабинет уже существует"
                        }
                    }
                },
            },

            500: {
                "description": "Ошибка при добавлении",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "Неизвестная ошибка добавлении кабинета"
                        }
                    }
                },
            },

        }
)
async def put_cabinet(
    session: SessionDep, # Сессия базы данных
    cabinet: str = Path(..., description="Кабнет", example="405-1")
) -> JSONResponse:
    logger.info(f"Запрос на вставку кабинета в базу данных. Кабинет: {cabinet}")

    adding: str | bool = await utils.put_cabinet(cabinet, session)

    if adding == "exists":
        logger.info("Кабинет уже существует. Отдаём ответ")
        return JSONResponse(content={"message": "Кабинет уже существует"}, status_code=409)
    elif adding:
        logger.info("Кабинет успешно добавлен. Отдаём ответ")
        return JSONResponse(content={"message": "Кабинет успешно добавлен"}, status_code=200)
    else:
        logger.error("ERROR add cabinet")
        return JSONResponse(content={"message": "Неизвестная ошибка добавлении кабинета"}, status_code=500)
    

@router_cabinet.delete(
        path="/remove/{cabinet}",
        description="Удалить кабинет",
        responses={
            200: {
                "description": "Успешное удаление",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "Кабинет успешно удалён"
                        }
                    }
                },
            },

            404: {
                "description": "Не найдено",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "Кабинет не найден"
                        }
                    }
                },
            },

            500: {
                "description": "Ошибка при удалении",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "Неизвестная ошибка удалении кабинета"
                        }
                    }
                },
            },
        }
)
async def remove_cabinet(
    session: SessionDep, # Сессия базы данных
    cabinet: str = Path(..., description="Кабнет", example="405-1")
) -> JSONResponse:
    logger.info(f"Запрос на удаление кабинета. Кабинет: {cabinet}")

    removing: bool | str = await utils.remove_cabinet(cabinet, session)

    if removing == "not found":
        logger.info("Кабинет не найден. Отдаём ответ")
        return JSONResponse(content={"message": "Кабинет не найден"}, status_code=404)
    elif removing:
        logger.info("Кабинет успешно удалён. Отдаём ответ")
        return JSONResponse(content={"message": "Кабинет успешно удалён"}, status_code=200)
    else:
        logger.error("Ошибка при удалении кабинета. Отдаём ответ")
        return JSONResponse(content={"message": "Неизвестная ошибка удалении кабинета"}, status_code=500)
    
