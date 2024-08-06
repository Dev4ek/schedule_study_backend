from fastapi import APIRouter, Path
from fastapi.responses import JSONResponse, FileResponse
from .. import utils
from loguru import logger
from app.core.dependencies import SessionDep

router_file = APIRouter(prefix="/file", tags=["Файлы"])

@router_file.get(
        path="/raspisanie.xls",
        description="Скачать файл raspisanie.xls",
        
)
async def get_groups(
    session: SessionDep # Сессия базы даныых
) -> JSONResponse:
    logger.info("Запрос на скачивание файла raspisanie.xls")

    getting = await utils.get_file_raspisanie(session)

    if getting:
        logger.info("Отдаём ответ файл")
        return FileResponse(path="raspisanie.xls", status_code=200)
    else:
        logger.error("Неизвестная ошибка при формировании файла. Оидаём ответ")
        return JSONResponse(content={"message": "Неизвестная ошибка при скачиваинии файла"}, status_code=500)
    

@router_file.put(
        path="/put/{group}",
        description="Добавить группу",
        responses={
            200: {
                "description": "Успешное добавление",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "Группа успешно добавлена"
                        }
                    }
                },
            },

            409: {
                "description": "Уже существует",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "Группа уже существует"
                        }
                    }
                },
            },

            500: {
                "description": "Ошибка при добавлении группы",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "Неизвестная ошибка при добавлении группы"
                        }
                    }
                },
            },
        }
)
async def put_group(
    session: SessionDep, # Сессия базы даных
    group: str = Path(..., description="Группа", example="Исп-232")
) -> JSONResponse:
    logger.info(f"Запрос на вставку группы. Группа: {group}")

    adding: bool | str = await utils.put_group(group, session)

    if adding == "exists":
        logger.info("Группа уже существует. Отдаём ответ")
        return JSONResponse(content={"message": "Группа уже существует"}, status_code=409)

    elif adding:
        logger.info("Группа успешно добавлена. Отдаём ответ")
        return JSONResponse(content={"message": "Группа успешно добавлена"}, status_code=200)

    else:
        logger.error("Неизвестная ошибка при добавлении группы. Отдаём ответ")
        return JSONResponse(content={"message": "Неизвестная ошибка при добавлении группы"}, status_code=500)
    


@router_file.delete(
        path="/remove/{group}",
        description="Удалить группу",
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
    
