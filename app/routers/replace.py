from fastapi import APIRouter, Depends, Query, Body,  Path
from fastapi.responses import JSONResponse
from .. import schemas, utils
from loguru import logger
from app.core.dependencies import SessionDep


router_replace = APIRouter(prefix="/replace", tags=["Замены"])




@router_replace.get(
        path="/all",
        summary="Список всех замен для групп",
)
async def get_all_replacements(
    session: SessionDep,
) -> JSONResponse:
    logger.info("Запрос на получение всех замен")

    getting: bool | schemas.Replace_output = await utils.all_replacemetns(session)

    if getting:
        logger.info("Отдаём ответ список замен")
        return JSONResponse(content=getting, status_code=200)
    else:
        logger.error("Отдаём ответ. Ошибка при получении замен")
        return JSONResponse(content={"message": "Неизвестная ошибка при получении списка замен"}, status_code=500)




@router_replace.get(
        path="/{group}",
        summary="Список всех замен для группу",
        responses={
            200: {
                "description": "Список замен",
                "content": {
                    "application/json": {
                        "example": 
                           {
                            "group": "Исп-232",
                            "date": "1 Августа",
                            "replacemetns": [
                                {
                                    "id": 3,
                                    "item": "Английский язые",
                                    "teacher": "Демиденко Наталья Ильинична",
                                    "cabinet": "36-2",
                                    "day": "Суббота",
                                    "num_lesson": 1
                                },
                                {
                                    "id": 4,
                                    "item": "Английский язык",
                                    "teacher": "Демиденко Н.И.",
                                    "cabinet": "405-1",
                                    "day": "Четверг",
                                    "num_lesson": 1
                                },
                                
                            ]
                        }
                    }
                },
            },

            500: {
                "description": "Ошибка установки",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "Неизвестная ошибка при получении списка групп"
                        }
                    }
                },
            },
        }
)
async def get_replacements(
    session: SessionDep,
    group: str = Path(..., description="Группа", example="Исп-232")
) -> JSONResponse:
    logger.info("Запрос на получение всех замен на группу {group}")

    getting: bool | schemas.Replace_output = await utils.replacemetns_group(group, session)

    if getting:
        logger.info("Отдаём ответ список замен")
        return JSONResponse(content=getting, status_code=200)
    else:
        logger.error("Отдаём ответ. Ошибка при получении замен")
        return JSONResponse(content={"message": "Неизвестная ошибка при получении списка замен"}, status_code=500)



@router_replace.put(
        path="/put",
        tags=["Замены"],
        summary="Добавить замену",
)
async def put_replace(
    session: SessionDep,
    payload: schemas.Replace_input = Body(..., description="Замена", example={
        "group": "Исп-232",
        "date": "23 Сентября",
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
        path="/remove",
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
        path="/remove/all",
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
async def remove_all_replace(
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
