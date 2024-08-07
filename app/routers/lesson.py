from fastapi import APIRouter, Depends, Path, Query, Body
from fastapi.responses import JSONResponse
from ..core import dependencies
from ..services import redis
from .. import schemas, utils
from loguru import logger
from app.core.dependencies import SessionDep

router_lesson = APIRouter(prefix="/lesson", tags=["Расписание"])

@router_lesson.get(
        path="/{lesson_id}",
        summary="Посмотреть информацию о паре по айди пары",
        response_model=schemas.Info_lesson_output
)
async def get_lesson_by_id(
    session: SessionDep, # Сессия базы данных
    lesson_id: int = Path(..., description="Айди пары", example=11)
) -> JSONResponse: 
    logger.info(f"Запрос на получение информации о паре по айди. Айди {lesson_id}")

    getting = await utils.get_lesson_by_id(lesson_id, session)

    if getting == "not found":
        logger.info(f"Отдаём ответ пара не найдена")
        return JSONResponse(content="Пара не найдена", status_code=200)
        
    elif getting:
        logger.info(f"Отдаём ответ информацию о паре")
        return JSONResponse(content=getting, status_code=200)
    
    else:
        logger.error(f"Неизвестная ошибка отдаём ответ")
        return JSONResponse(content={"message": "Неизвестная ошибка получении информации"}, status_code=500)



@router_lesson.put(
        path="/put",
        summary="Установить пару для группы",
        responses={
            200: {
                "description": "Успешная установка",
                "content": {
                    "application/json": {
                        "example": 
                           {
                                "message": "Пара для группы успешно установлена"                               
                           }
                    }
                },
            },

            500: {
                "description": "Ошибка установки",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "Неизвестная ошибка при установке пары"
                        }
                    }
                },
            },

        }
)
async def put_lesson(
    session: SessionDep, # Сессия базы данных
    payload: schemas.Lesson_input = Body(..., description="Данные для добавления пары",
    example={
        "group": "Исп-232",
        "day": "Понедельник",
        "item": "Русский язык",
        "num_lesson": 2,
        "teacher": "Вартабедьян Виктория Борисовна",
        "cabinet": "405-1",
        "week": 0
    }
),
) -> JSONResponse: 
    logger.info(f"Запрос на установку расписания. Payload: {payload.model_dump_json()}")

    setting: bool = await utils.put_lesson(payload, session)

    if setting:
        logger.info(f"Отдаём ответ. Пара успешно установлена")
        return JSONResponse(content={'message': "Пара для группы успешно установлена"}, status_code=200)
    
    else:
        logger.error(f"Пара для группы не была установлена. Отдаём ответ")
        return JSONResponse(content={"message": "Неизвестная ошибка при установке пары"}, status_code=500)



@router_lesson.delete(
        path="/remove",
        summary="Удалить пару",
        responses={
            200: {
                "description": "Успешное удаление",
                "content": {
                    "application/json": {
                        "example": 
                           {
                                "message": "Пара успешно удалена"                               
                           }
                    }
                },
            },

            500: {
                "description": "Ошибка удаления",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "Неизвестная ошибка при удалении пары"
                        }
                    }
                },
            },
        }
)
async def remove_lesson(
    session: SessionDep, # Сессия базы данных
    payload: schemas.Remove_lesson = Body(..., description="Данные для удаления пары",
    example={
        "group": "Исп-232",
        "day": "Понедельник",
        "num_lesson": 0,
        "week": 0
    })
) -> JSONResponse: 
    logger.info(f"Запрос на удаление пары. Payload: {payload.model_dump_json()}")

    removing: bool = await utils.remove_lesson(payload, session)

    if removing:
        return JSONResponse(content={'message': "Пара успешно удалена"}, status_code=200)
    
    else:
        logger.error(f"Отдаём ответ ошибка при удалении")
        return JSONResponse(content={"message": "Неизвестная ошибка при удалении пары"}, status_code=500)
