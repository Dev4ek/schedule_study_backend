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
async def check_installed_replace(
    session: SessionDep,
    num_lesson: int = Query(..., description="Номер пары", ge=0, le=2, example=2),
    cabinet: str = Query(..., description="Кабинет где будет проходить пара", example="405-1"),
    date: str = Query(..., description="Дата замены", example="23 Сентября")
) -> JSONResponse:
    logger.info(f"Запрос проверку установлена ли замена. Кабинет: {cabinet}, номер пары: {num_lesson}, дата: {date}")
       
    logger.debug("Делаем запрос в бд")
    result = await session.execute(
        db.select(db.table.Replacements)
        .filter_by(
                    num_lesson=num_lesson,
                    cabinet=cabinet,
                    date=date
            )
    )

    replace_info = result.scalars().first()

    logger.info("Формируем pydantic model и возвращаем")
    form_json = None
    if replace_info:
        form_json = schemas.Replace_full_info(
                replace_id = replace_info.id,
                group = replace_info.group,
                date = replace_info.date,
                num_lesson = replace_info.num_lesson,
                cabinet = replace_info.cabinet,
                item = replace_info.item,
                teacher = replace_info.teacher,
        )  
        
    replace_info_model = schemas.Replace_check(
        use=True if form_json else False,
        replace=form_json
        )

    return JSONResponse(content=replace_info_model.model_dump(), status_code=200)






@router_replace.get(
        path="/date",
        summary="Посмотреть дату замен",
)
async def get_date(
    session: SessionDep,
) -> JSONResponse:
    logger.info(f"Запрос просмотр даты замен")

    logger.debug("Делаем запрос в бд")
    result = await session.execute(db.select(db.table.Depends.date_replacements))
    result_date = result.scalar()

    logger.info("Возвращаем дату")
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
    logger.info(f"Запрос на получение информации о замене по айди. Айди замены: {replace_id}")

    logger.debug("Выполняем запрос в бд")
    result = await session.execute(
        db.select(db.table.Replacements)
        .filter_by(
                    id=replace_id,
            )
    )
    replace_info = result.scalars().first()
    
    if not replace_info:
        logger.info("Замена не найдена. Отдаём ответ")
        return JSONResponse(content={"message": "Замена не найдена"}, status_code=404)
    
    
    logger.info("Формируем модель pydantic и вовзращаем")
    replace_info_model = schemas.Replace_full_info(
            replace_id = replace_info.id,
            group = replace_info.group,
            date = replace_info.date,
            num_lesson = replace_info.num_lesson,
            cabinet = replace_info.cabinet,
            item = replace_info.item,
            teacher = replace_info.teacher,
    )  

    return JSONResponse(content=replace_info_model.model_dump(), status_code=200)
    
    
    
    
    
    
    
    

@router_replace.get(
        path="/group/{group}",
        summary="Посмотреть замены для группы",
        response_model=schemas.Replace_out
)
async def get_replacements(
    session: SessionDep,
    group: str = Path(..., description="Группа", example="Исп-232"),
    date: str = Query(..., description="Дата замены", example="23 Сентября")
) -> JSONResponse:
    logger.info(f"Запрос на получение всех замен для группы {group}, дата: {date}")

    logger.debug("Выполняем запрос в бд")
    result = await session.execute(
            db.select(db.table.Replacements)
            .filter_by(
                        group=group,
                        date=date
                )
        )
    results = result.all()

    logger.info("Формируем модель pydantic и вовзращаем")
    list_replacements = []
    
    for data_replace in results:
        for replace in data_replace:
            list_replacements.append(schemas.Replace_lesson(
                replace_id = replace.id,
                num_lesson = replace.num_lesson,
                item = replace.item,
                teacher = replace.teacher,
                cabinet = replace.cabinet,
            ).model_dump())
    
    replacements_model = schemas.Replace_out(
        group=group,
        date=date,
        replacements=list_replacements
    )

    return JSONResponse(content=replacements_model.model_dump(), status_code=200)







@router_replace.get(
        path="/teacher/{teacher}",
        summary="Посмотреть замены для учителя",
        response_model=schemas.Replace_teacher_out
)
async def get_replacements(
    session: SessionDep,
    teacher: str = Path(..., description="Учитель", example="Демиденко Наталья Ильинична"),
    date: str = Query(..., description="Дата замены", example="23 Сентября")
) -> JSONResponse:
    logger.info(f"Запрос на получение всех замен для учителя {teacher}, дата: {date}")


    logger.debug("Выполняем запрос в бд")
    result = await session.execute(
            db.select(db.table.Replacements)
            .filter_by(
                        teacher=teacher,
                        date=date
                )
        )
    results = result.all()

    logger.info("Формируем модель pydantic и вовзращаем")
    list_replacements = []
    
    for data_replace in results:
        for replace in data_replace:
            list_replacements.append(schemas.Replace_lesson_teacher(
                replace_id = replace.id,
                num_lesson = replace.num_lesson,
                item = replace.item,
                group = replace.group,
                cabinet = replace.cabinet,
            ).model_dump())
    
    replacements_model = schemas.Replace_teacher_out(
        teacher=teacher,
        date=date,
        replacements=list_replacements,
    )

    return JSONResponse(content=replacements_model.model_dump(), status_code=200)
 







@router_replace.post(
        path="",
        summary="Установить или изменить замену",
        response_model=schemas.Replace_id
        
)
async def put_replace(
    session: SessionDep,
    payload: schemas.Replace_in = Body(..., description="Замена", example={
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

    logger.debug("Делаем запрос в бд")
    replace_id = await session.execute(
                db.select(db.table.Replacements.id)
                .filter_by(
                            group=payload.group,
                            num_day=schemas.Day_to_num[payload.day],
                            num_lesson=payload.num_lesson,
                            date=payload.date
                
                )
    )
    exists_replace = replace_id.scalar_one_or_none()

    if exists_replace:
        logger.debug("Замена существует. Формируем запрос на изменение замены")
        query = (
            db.update(
                db.table.Replacements
            )
            .values(
                item=payload.item,
                teacher=payload.teacher,
                cabinet=payload.cabinet,
            )
            .filter_by(
                    group=payload.group,
                    num_day=schemas.Day_to_num[payload.day],
                    num_lesson=payload.num_lesson,
                    date=payload.date,
            )
            .returning(db.table.Replacements.id)
        )

    else:
        logger.debug("Замена не существует. Формируем запрос на добавление замены")

        query = (
            db.insert(db.table.Replacements)
            .values(
                group=payload.group,
                num_day=schemas.Day_to_num[payload.day],
                num_lesson=payload.num_lesson,
                item=payload.item,
                teacher=payload.teacher,
                cabinet=payload.cabinet,
                date=payload.date,
            )
            .returning(db.table.Replacements.id)
        )

    logger.debug("Делаем запрос в бд")
    result = await session.execute(query)
    replace_id = result.scalar()
    await session.commit()

    logger.info("Формируем модель pydantic и вовзращаем")
    
    repalce_id_model = schemas.Replace_id(replace_id=replace_id)

    return JSONResponse(content=repalce_id_model.model_dump(), status_code=200)








@router_replace.delete(
        path="",
        summary="Удалить замену",
        description="При удалении возвращает True, Если удалено 0 замен то возвращает False"
)
async def remove_replace(
    session: SessionDep,
    payload: schemas.Replace_remove = Body(..., description="Параметры замены", example={
        "group": "Исп-232",
        "date": "23 Сентября",
        "day": "Понедельник",
        "num_lesson": 1,
    })
) -> JSONResponse:
    logger.info(f"Запрос на удаление замены. Payload: {payload.model_dump_json()}")

    logger.debug("Выполняем запрос в бд")
    result = await session.execute(
         db.delete(db.table.Replacements)
        .filter(
                db.table.Replacements.group == payload.group,
                db.table.Replacements.num_day == schemas.Day_to_num[payload.day],
                db.table.Replacements.num_lesson == payload.num_lesson,
                db.table.Replacements.date == payload.date,
        )
    )
    await session.commit()

    if result.rowcount > 0:
        logger.info("Замена успешно удалена. Возвращаем True")                    
        return JSONResponse(content=True, status_code=200)
    else:
        return JSONResponse(content=False, status_code=404)



@router_replace.delete(
        path="/all",
        summary="Удалить все замены",
        description="При удалении возвращает True"
)
async def delete_all(
    session: SessionDep,
) -> JSONResponse:
    logger.info(f"Запрос на удаление всех замен.")


    logger.debug("Выполняем запрос в бд")
    await session.execute(
                        query_delete = (
                        db.delete(db.table.Replacements)
                    )
        )
    await session.commit()
    
    logger.info("Все замены успешно удалены. Возвращаем True")
    return JSONResponse(content=True, status_code=200)




@router_replace.delete(
        path="/{replace_id}",
        summary="Удалить замену по айди",
        description="При удалении возвращает True, Если удалено 0 замен то возвращает False"

)
async def remove_replace(
    session: SessionDep,
    replace_id: int = Path(..., description="айди замены", example=5)
) -> JSONResponse:
    logger.info(f"Запрос на удаление замены по айди. Айди замены {replace_id}")

    logger.debug("Выполняем запрос в бд")
    result = await session.execute(db.delete(db.table.Replacements).filter_by(id=replace_id))
    await session.commit()

    if result.rowcount > 0:
        logger.info("Замена успешно удалена. Возвращаем True")                    
        return JSONResponse(content=True, status_code=200)
    else:
        logger.info("Замена не найдена. Возвращаем False")                    
        return JSONResponse(content=False, status_code=404)

    
    


@router_replace.put(
        path="/date/{date}",
        summary="Изменить дату замен",
)
async def set_date(
    session: SessionDep,
    date: str = Path(..., title="Дата замен", description="Дата установки замен", example="23 Сентября")
) -> JSONResponse:
    logger.info(f"Запрос на установку даты замен")

    logger.debug("Делаем запрос в бд")
    await session.execute(
                db.update(db.table.Depends)
                .values(date_replacements=date)
    )
    await session.commit()
    logger.info("Успешно изменено. Возвращает True")
    return JSONResponse(content=True, status_code=200)

