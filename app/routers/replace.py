from fastapi import APIRouter, Depends, Query, Body,  Path
from fastapi.responses import JSONResponse
from .. import schemas, utils
from loguru import logger
from app.core.dependencies import SessionDep
from ..services import database as db


router_replace = APIRouter(prefix="/replace", tags=["Замены"])


@router_replace.get(
        path="/check",
        summary="Посмотреть установлена ли замена",
        response_model=schemas.Replace_check
)
async def get_date(
    session: SessionDep,
    num_lesson: int = Query(..., description="Номер пары", ge=0, le=2, example=2),
    cabinet: str = Query(..., description="Кабинет где будет проходить пара", example="405-1")
) -> JSONResponse:
    logger.info(f"Запрос проверку установлена ли замена. Кабинет: {cabinet}, номер пары: {num_lesson}")

    gettting: bool | schemas.Replace_check = await utils.repalce_check(num_lesson, cabinet, session)
    
    if gettting:
        logger.info(f"Отдаём ответ информацию о замене")
        return JSONResponse(content=gettting.model_dump(), status_code=200)
    else:
        logger.info("Отдаём ответ ошибка при проверке замены")
        return JSONResponse(content={"message": "Неизвестнеая ошибка при проверке замены"}, status_code=500)
            
        

   



@router_replace.get(
        path="/date",
        summary="Посмотреть дату замен",
)
async def get_date(
    session: SessionDep,
) -> JSONResponse:
    logger.info(f"Запрос просмотр даты замен")

    result = await session.execute(db.select(db.table.Depends.date_replacements))
    result_date = result.scalar()

    return JSONResponse(content={"date": result_date}, status_code=200)
   

@router_replace.get(
        path="/{replace_id}",
        summary="Посмотреть информацию о замене по айди",
        response_model=schemas.Replace_full_info
)
async def get_replacements(
    session: SessionDep,
    replace_id: int = Path(..., description="Айди замены", example=21)
) -> JSONResponse:
    logger.info(f"Запрос на получение информации о замене по айди {replace_id}")

    getting: str | bool | schemas.Replace_full_info = await utils.info_replace_by_id(replace_id, session)

    if getting == "Замена не найдена":
        logger.info("Отдаём ответ замена не найдена")
        return JSONResponse(content={"message": "Замена не найдена"}, status_code=404)
    if getting:
        logger.info("Отдаём ответ данные о замене")
        return JSONResponse(content=getting, status_code=200)
    else:
        logger.error("Отдаём ответ. Ошибка при получении замен")
        return JSONResponse(content={"message": "Неизвестная ошибка при получении списка замен"}, status_code=500)


@router_replace.get(
        path="/group/{group}",
        summary="Посмотреть замены для группы",
        response_model=schemas.Replace_out
)
async def get_replacements(
    session: SessionDep,
    group: str = Path(..., description="Группа", example="Исп-232")
) -> JSONResponse:
    logger.info(f"Запрос на получение всех замен на группу {group}")

    getting: bool | schemas.Replace_out = await utils.replacemetns_group(group, session)

    if getting:
        logger.info("Отдаём ответ список замен")
        return JSONResponse(content=getting, status_code=200)
    else:
        logger.error("Отдаём ответ. Ошибка при получении замен")
        return JSONResponse(content={"message": "Неизвестная ошибка при получении списка замен"}, status_code=500)


@router_replace.get(
        path="/teacher/{teacher}",
        summary="Посмотреть замены для учителя",
        response_model=schemas.Replace_teacher_out
)
async def get_replacements(
    session: SessionDep,
    teacher: str = Path(..., description="Учитель", example="Демиденко Наталья Ильинична")
) -> JSONResponse:
    logger.info(f"Запрос на получение всех замен для учителя {teacher}")

    getting: bool | schemas.Replace_teacher_out = await utils.replacemetns_teacher(teacher, session)

    if getting:
        logger.info("Отдаём ответ список замен для учителя")
        return JSONResponse(content=getting, status_code=200)
    else:
        logger.error("Отдаём ответ. Ошибка при получении замен для учителя")
        return JSONResponse(content={"message": "Неизвестная ошибка при получении списка замен"}, status_code=500)



@router_replace.post(
        path="",
        tags=["Замены"],
        summary="Установить или изменить замену",
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
        path="",
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
        summary="Удалить замену по айди",
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
    replace_id: int = Path(..., description="айди замены", example=5)
) -> JSONResponse:
    logger.info(f"Запрос на удаление замены по")

    removing: bool = await utils.remove_replace_by_id(replace_id, session)

  
    if removing:
        logger.info("Замена успешно удалена. Отдаём ответ")
        return JSONResponse(content={"message": "Замена успешно удалена"}, status_code=200)
    else:
        logger.error("Неизвестная ошибка при удалении . Отдаём ответ")
        return JSONResponse(content={"message": "Неизвестная ошибка удалении замены"}, status_code=500)



@router_replace.put(
        path="/date/{date}",
        summary="Изменить дату замен",
)
async def set_date(
    session: SessionDep,
    date: str = Path(..., title="Дата замен", description="Дата установки замен", example="23 Сентября")
) -> JSONResponse:
    logger.info(f"Запрос на установку даты замен")

    setting: bool = await utils.set_date_replacements(date, session)

    if setting:
        logger.info("Дата для замен успешно установлена. Отдаём ответ")
        return JSONResponse(content={"message": "Дата успешно установлена"}, status_code=200)
    else:
        logger.error("Неизвестная ошибка при установке даты замен")
        return JSONResponse(content={"message": "Неизвестная ошибка установке даты для замен"}, status_code=500)


