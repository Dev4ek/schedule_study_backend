from fastapi import APIRouter, Depends, Path, Query, Body
from fastapi.responses import JSONResponse
from .. import schemas, utils
from loguru import logger
from app.core.dependencies import SessionDep

router_teacher = APIRouter(prefix="/teacher", tags=["Учителя"])


# @router_teacher.get(
#         path="/lessons",
#         description="Расписание для учителя"
# )
# async def get_teachers(
#     session: SessionDep,
#     teacher: str = Query(..., description="ФИО учителя", example="Демиденко Наталья Ильинична"),
# ) -> JSONResponse:
#     logger.info(f"Запрос на расписание для учителя. Учитель {teacher}")

#     getting: str | bool = await utils.all_teachers(session)

#     if getting:
#         logger.info("Отдаём ответ список учителей")
#         return JSONResponse(content=getting, status_code=200)
    
#     else:
#         logger.error("Ошибка при получении списка. Отдаём ответ")
#         return JSONResponse(content={"message": "Неизвестная ошибка при получении списка учителей"}, status_code=500)
    






@router_teacher.get(
        path="/all",
        summary="Список всех учителей",
        responses={
            200: {
                "description": "Список учителей",
                "content": {
                    "application/json": {
                        "example": 
                        [
                            {
                                "teacher_id": 1,
                                "teacher": "Демиденко Наталья Ильинична"
                            },
                            {
                                "teacher_id": 3,
                                "teacher": "Вартабедьян Виктория Борисовна"
                            }
                            ]
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
async def get_teachers(
    session: SessionDep
) -> JSONResponse:
    logger.info("Запрос на список всех учителей")

    getting: str | bool = await utils.all_teachers(session)

    if getting:
        logger.info("Отдаём ответ список учителей")
        return JSONResponse(content=getting, status_code=200)
    
    else:
        logger.error("Ошибка при получении списка. Отдаём ответ")
        return JSONResponse(content={"message": "Неизвестная ошибка при получении списка учителей"}, status_code=500)
    


@router_teacher.put(
        path="/put/{teacher}",
        summary="Добавить учителя",
        responses={
            200: {
                "description": "Успешно добавлен",
                "content": {
                    "application/json": {
                        "example": 
                        {
                            "message": "Учитель успешно добавлен"
                        }
                          
                    }
                },
            },
            409: {
                "description": "Уже существует",
                "content": {
                    "application/json": {
                        "example": 
                        {
                            "message": "Учитель с таким ФИО уже существует"
                        }
                          
                    }
                },
            },

            500: {
                "description": "Ошибка добавления",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "Неизвестная ошибка добавлении учителей"
                        }
                    }
                },
            },
        }
)
async def put_teacher(
    session: SessionDep,
    teacher: str = Path(..., description="ФИО учителя", example="Демиденко Наталья Ильинична")
) -> JSONResponse:
    logger.info(f"Запрос на добавление учителя {teacher}")

    adding: str | bool = await utils.put_teacher(teacher, session)

    if adding == "exists":
        logger.info("Учитель с таким ФИО уже существует. Отдаём ответ")
        return JSONResponse(content={"message": "Учитель с таким ФИО уже существует"}, status_code=409)
    elif adding:
        logger.info("Учитель успешно добавлен. Отдаём ответ")
        return JSONResponse(content={"message": "Учитель успешно добавлен"}, status_code=200)
    else:
        logger.error("Произошла ошибка при добавлении учителя. Возвращаем ответ")
        return JSONResponse(content={"message": "Неизвестная ошибка добавлении учителей"}, status_code=500)


@router_teacher.delete(
        path="/remove/{teacher}",
        summary="Удалить учителя",
        responses={
            200: {
                "description": "Успешно удален",
                "content": {
                    "application/json": {
                        "example": 
                        {
                            "message": "Учитель успешно удалён"
                        }
                          
                    }
                },
            },
            404: {
                "description": "Не найден",
                "content": {
                    "application/json": {
                        "example": 
                        {
                            "message": "Учитель с таким ФИО не найден"
                        }
                          
                    }
                },
            },

            500: {
                "description": "Ошибка удаления",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "Неизвестная ошибка удалении учителя"
                        }
                    }
                },
            },
        }
)
async def remove_teacher(
    session: SessionDep,
    teacher: str = Path(..., description="ФИО учителя", example="Демиденко Наталья Ильинична")
) -> JSONResponse:
    logger.info(f"Запрос на удаление учителя из бд {teacher}")

    removing: bool | str = await utils.remove_teacher(teacher, session)

    if removing == "not found":
        logger.info("Учитель с таким ФИО не найден. Вовзвращаем ответ")
        return JSONResponse(content={"message": "Учитель с таким ФИО не найден"}, status_code=404)
    elif removing:
        logger.info("Учитель успешно удалён. Вовзвращаем ответ")
        return JSONResponse(content={"message": "Учитель успешно удалён"}, status_code=200)
    else:
        logger.error("Ошибка удалении учителя. Вовзвращаем ответ")
        return JSONResponse(content={"message": "Неизвестная ошибка удалении учителя"}, status_code=500)