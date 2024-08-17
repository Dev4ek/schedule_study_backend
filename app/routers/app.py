from typing import Any
from fastapi import APIRouter, Depends, Path, Query, Body
from fastapi.responses import JSONResponse
from ..core import dependencies
from ..services import redis
from .. import schemas, utils
from loguru import logger
from app.core.dependencies import SessionDep


router_app = APIRouter(prefix="/app", tags=["Приложение"])

@router_app.get(
        path="/group/{group}", 
        dependencies=[Depends(dependencies.verify_version)],
        summary="Посмотреть расписание для группы",
        response_model=schemas.Schedule_app_output,
)
async def get_lessons(
    session: SessionDep, # Сессия базы данных
    group: str = Path(..., description="Группа", example="Исп-232"),
) -> JSONResponse: 
    logger.info(f"Запрос на получения расписания для группы. Группа: {group}")

    cache_schedule: dict | bool = await redis.check_lessons(group)

    if cache_schedule:
        logger.debug(f"Расписание есть в кеше redis")

        logger.debug("Формируем ответ в pydantic model")
        cache_schedule_model = schemas.Schedule_app_output(**cache_schedule).model_dump()
        
        logger.info(f"Вовзращаем сформированнное json расписание для группы. Группа: {group}")
        return JSONResponse(content=cache_schedule_model, status_code=200)

    logger.debug(f"Расписание не найдено в кеше redis. Запускем функцию формирования расписания")
    schedule: bool | schemas.Schedule_app_output = await utils.get_lessons_app(group, session)

    if schedule:
        logger.debug("Устанавливаем сформированное расписание в кеш redis")
        await redis.set_lesssons(group, schedule)

        logger.debug("Отдаём ответ сформированное расписание")
        return JSONResponse(content=schedule, status_code=200)
    
    else:
        logger.error(f"Ошибка при получении расписания. Отдаём ответ. Группа: {group}")
        return JSONResponse(content={"message": "Неизвестная ошибка при получении расписания"}, status_code=500)


@router_app.get(
        path="/teacher/{teacher}",
        summary="Посмотреть расписание для учителя",
        response_model=schemas.Schedule_teacher_out
       
)
async def get_lesson_for_teacher(
    session: SessionDep, # Сессия базы данных
    teacher: str = Path(..., description="ФИО учителя", example="Демиденко Наталья Ильинична")
) -> JSONResponse:
    logger.info(f"Запрос на расписание для учителя. Учитель {teacher}")
    
    cache_schedule: dict | bool = await redis.check_lessons(teacher)

    if cache_schedule:
        logger.debug(f"Расписание есть в кеше redis")

        logger.debug("Формируем ответ в pydantic model")
        cache_schedule_model = schemas.Schedule_teacher_out(**cache_schedule).model_dump()
        
        logger.info(f"Вовзращаем сформированнное json расписание для учиттеля. Учитель: {teacher}")
        return JSONResponse(content=cache_schedule_model, status_code=200)

    logger.debug(f"Расписание не найдено в кеше redis. Запускем функцию формирования расписания")
    getting: schemas.Schedule_teacher_out | bool = await utils.get_lessons_teacher_app(teacher, session)

    if getting:
        logger.debug("Устанавливаем сформированное расписание в кеш redis")
        await redis.set_lesssons(teacher, getting)
        
        logger.info(f"Отдаём ответ. Список пар учителю")
        return JSONResponse(content=getting, status_code=200)
    
    else:
        logger.error(f"Отдаём ответ произошла ошибка при получении пар учителю")
        return JSONResponse(content={"message": "Неизвестная ошибка при получении пар"}, status_code=500)


