from fastapi import APIRouter, Depends, Query, Body,  Path
from fastapi.responses import JSONResponse
from .. import schemas, utils
from loguru import logger
from app.core.dependencies import SessionDep


router_replace = APIRouter(prefix="/replace", tags=["Замены"])




@router_replace.get(
        path="/all",
        summary="Список всех замен для групп",
        response_model=schemas.Replacements_all_out
)
async def get_all_replacements(
    session: SessionDep,
) -> JSONResponse:
    logger.info("Запрос на получение всех замен")

    getting: bool | schemas.Replacements_all_out = await utils.all_replacemetns(session)

    if getting:
        logger.info("Отдаём ответ список замен")
        return JSONResponse(content=getting, status_code=200)
    else:
        logger.error("Отдаём ответ. Ошибка при получении замен")
        return JSONResponse(content={"message": "Неизвестная ошибка при получении списка замен"}, status_code=500)




@router_replace.get(
        path="/{group}",
        summary="Список замен для группы",
        response_model=schemas.Replace_out
)
async def get_replacements(
    session: SessionDep,
    group: str = Path(..., description="Группа", example="Исп-232")
) -> JSONResponse:
    logger.info("Запрос на получение всех замен на группу {group}")

    getting: bool | schemas.Replace_out = await utils.replacemetns_group(group, session)

    if getting:
        logger.info("Отдаём ответ список замен")
        return JSONResponse(content=getting, status_code=200)
    else:
        logger.error("Отдаём ответ. Ошибка при получении замен")
        return JSONResponse(content={"message": "Неизвестная ошибка при получении списка замен"}, status_code=500)


@router_replace.put(
        path="/",
        tags=["Замены"],
        summary="Добавить или изменить замену",
)
async def put_replace(
    session: SessionDep,
    payload: schemas.Replace_in = Body(..., description="Замена", example={
        "group": "Исп-232",
        "day": "Понедельник",
        "item": "Русский язык",
        "num_lesson": 1,
        "teacher": "Вартабедьян Виктория Борисовна",
        "cabinet": "36-2"
    })
) -> JSONResponse:
    
    logger.info(f"Запрос на вставку замены {payload.model_dump_json()}")

    adding: bool = await utils.put_replace(payload, session)

    if adding:
        logger.info("Замена успешно добавлена. Отдаём ответ")
        return JSONResponse(content={"message": "Замена успешно добавлена"}, status_code=200)
    else:
        logger.error("Ошибка при добавлении замены. Отдаём ответ")
        return JSONResponse(content={"message": "Неизвестная ошибка при добавлении замены"}, status_code=500)


@router_replace.delete(
        path="/",
        summary="Удалить замену",
        responses={
            200: {
                "description": "Успешное удаление",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "Замена успешно удалена"
                        }
                    }
                },
            },

            404: {
                "description": "Не найдена",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "Замена не найдена"
                        }
                    }
                },
            },

            500: {
                "description": "Ошибка при удалении замены",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "Неизвестная ошибка удалении замены"
                        }
                    }
                },
            },
        },
)
async def remove_replace(
    session: SessionDep,
    payload: schemas.Replace_remove = Body(..., description="Параметры замены", example={
        "group": "Исп-232",
        "day": "Понедельник",
        "num_lesson": 1,
    })
) -> JSONResponse:
    logger.info(f"Запрос на удаление замены. Payload: {payload.model_dump_json()}")

    removing: bool | str = await utils.remove_replace(payload, session)

    if removing == "not found":
        logger.info("Замена не найдена. Отдаём ответ")
        return JSONResponse(content={"message": "Замена не найдена"}, status_code=404)
    elif removing:
        logger.info("Замена успешно удалена. Отдаём ответ")
        return JSONResponse(content={"message": "Замена успешно удалена"}, status_code=200)
    else:
        logger.error("Неизвестная ошибка при удалении . Отдаём ответ")
        return JSONResponse(content={"message": "Неизвестная ошибка удалении замены"}, status_code=500)




@router_replace.delete(
        path="/all",
        summary="Удалить все замены",
        responses={
            200: {
                "description": "Успешное удаление всех замен",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "Все замены были удалены"
                        }
                    }
                },
            },


            500: {
                "description": "Ошибка при удалении всех замен",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "Неизвестная ошибка удалении всех замен"
                        }
                    }
                },
            },
        },
)
async def delete_all(
    session: SessionDep,
) -> JSONResponse:
    logger.info(f"Запрос на удаление всех замен.")

    removing: bool = await utils.remove_all_replacements(session)

    if removing:
        logger.info("Все замены успешно удалены. Отдаём ответ")
        return JSONResponse(content={"message": "Все замены были удалены"}, status_code=200)
    else:
        logger.error("Неизвестная ошибка при удалении всех замен. Отдаём ответ")
        return JSONResponse(content={"message": "Неизвестная ошибка удалении всех замен"}, status_code=500)


@router_replace.delete(
        path="/{replace_id}",
        summary="Удалить замену",
        responses={
            200: {
                "description": "Успешное удаление",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "Замена успешно удалена"
                        }
                    }
                },
            },

            404: {
                "description": "Не найдена",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "Замена не найдена"
                        }
                    }
                },
            },

            500: {
                "description": "Ошибка при удалении замены",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "Неизвестная ошибка удалении замены"
                        }
                    }
                },
            },
        },
)
async def remove_replace(
    session: SessionDep,
    payload: schemas.Replace_remove = Body(..., description="Параметры замены", example={
        "group": "Исп-232",
        "day": "Понедельник",
        "num_lesson": 1,
    })
) -> JSONResponse:
    logger.info(f"Запрос на удаление замены. Payload: {payload.model_dump_json()}")

    removing: bool | str = await utils.remove_replace(payload, session)

    if removing == "not found":
        logger.info("Замена не найдена. Отдаём ответ")
        return JSONResponse(content={"message": "Замена не найдена"}, status_code=404)
    elif removing:
        logger.info("Замена успешно удалена. Отдаём ответ")
        return JSONResponse(content={"message": "Замена успешно удалена"}, status_code=200)
    else:
        logger.error("Неизвестная ошибка при удалении . Отдаём ответ")
        return JSONResponse(content={"message": "Неизвестная ошибка удалении замены"}, status_code=500)



@router_replace.put(
        path="/date/{date}",
        summary="Установить дату замен",
)
async def set_date(
    session: SessionDep,
    date: str = Path(..., title="Дата замен", description="Дата установки замен", example="23 Сентября")
) -> JSONResponse:
    logger.info(f"Запрос на удаление всех замен.")



    # if removing:
    #     logger.info("Все замены успешно удалены. Отдаём ответ")
    #     return JSONResponse(content={"message": "Все замены были удалены"}, status_code=200)
    # else:
    #     logger.error("Неизвестная ошибка при удалении всех замен. Отдаём ответ")
    #     return JSONResponse(content={"message": "Неизвестная ошибка удалении всех замен"}, status_code=500)
