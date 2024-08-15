from ..services import database as db
from loguru import logger
from .. import schemas
from app import schemas
from app.core.dependencies import SessionDep
from icecream import ic


async def repalce_check(
        num_lesson: int, # number of lesson
        cabinet: str, # cabinet example "405-1"
        session: SessionDep, # Сессия базы данных
):
    try:
        logger.debug(f"Формируем запрос на проверку существующей замены")
        query_check = (
            db.select(db.table.Replacements)
            .filter_by(
                        num_lesson=num_lesson,
                        cabinet=cabinet,
                )
        )

        logger.debug("Делаем запрос в бд")
        result = await session.execute(query_check)

        replace_info = result.scalars().first()

        form_json = None
        if replace_info:
            form_json = {
                    "replace_id": replace_info.id,
                    "group": replace_info.group,
                    "num_lesson": replace_info.num_lesson,
                    "cabinet": replace_info.cabinet,
                    "item": replace_info.item,
                    "teacher": replace_info.teacher,
                }   
            
        logger.debug("Формируем модель pydantic")
        output_model = schemas.Replace_check(
            use=True if form_json else False,
            replace=schemas.Replace_full_info(**form_json) if form_json else None 
            )

        logger.debug("Успешно выполнено. Вовзращаем модель")
        return output_model

    except Exception:
        logger.exception(f"Произошла ошибка при добавлении замены в бд")
        return False
    








async def put_replace(
        payload: schemas.Replace_in,
        session: SessionDep, # Сессия базы данных
) -> bool:
    try:
        logger.debug(f"Формируем запрос на проверку существующей замены")
        query_check = (
            db.select(db.table.Replacements.id)
            .filter_by(
                        group=payload.group,
                        num_day=schemas.Day_to_num[payload.day],
                        num_lesson=payload.num_lesson,
                )
        )

        logger.debug("Делаем запрос в бд")
        result = await session.execute(query_check)

        logger.debug("Получаем результат scalar_one_or_none")
        exists_replace = result.scalar_one_or_none()

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
                )
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
                )
            )

        logger.debug("Делаем запрос в бд")
        await session.execute(query)
        await session.commit()

        logger.debug("Успешно выполнено. Вовзращаем True")
        return True

    except Exception:
        logger.exception(f"Произошла ошибка при добавлении замены в бд")
        return False
    



async def set_date_replacements(
        date: str, # example: "23 Сентября"
        session: SessionDep, # Сессия базы данных
) -> bool:
    try:
        query = (
            db.update(db.table.Depends)
            .values(date_replacements=date)
        )
           
        logger.debug("Делаем запрос в бд")
        await session.execute(query)
        await session.commit()

        logger.debug("Успешно выполнено. Вовзращаем True")
        return True

    except Exception:
        logger.exception(f"Произошла ошибка при добавлении замены в бд")
        return False
    



async def replacemetns_group(
        group: str, # example "Исп-232"
        session: SessionDep # Сессия базы данных
) -> schemas.Replace_out | bool:
    try:
        logger.debug("Формируем запрос в бд")

        query_select = (
            db.select(db.table.Replacements)
            .filter_by(
                        group=group,
                )
        )

        logger.debug("Выполняем запрос в бд")
        result = await session.execute(query_select)

        logger.debug("Получаем данные")
        results = result.all()

        logger.debug("Формируем json ответ")
        list_replacements = []
        
        result_date = await session.execute(db.select(db.table.Depends.date_replacements))
        date_replacements = result_date.scalar()
        
        for data_replace in results:
            for replace in data_replace:
                list_replacements.append({
                    "replace_id": replace.id,
                    "num_lesson": replace.num_lesson,
                    "item": replace.item,
                    "teacher": replace.teacher,
                    "cabinet": replace.cabinet,
                })
        
        output_json = {
            "group": group,
            "date": date_replacements,
            "replacements": list_replacements,
        }

        logger.debug("Формируем модель pydantic и вовзращаем")
        output_json_model = schemas.Replace_out(**output_json).model_dump()
        
        return output_json_model
    except Exception:
        logger.exception(f"Произошла ошибка при получении замен")
        return False





async def replacemetns_teacher(
        teacher: str, # example "Демиденко Наталья Ильинична
        session: SessionDep # Сессия базы данных
):
    try:
        logger.debug("Формируем запрос в бд")

        query_select = (
            db.select(db.table.Replacements)
            .filter_by(
                        teacher=teacher,
                )
        )

        logger.debug("Выполняем запрос в бд")
        result = await session.execute(query_select)

        logger.debug("Получаем данные")
        results = result.all()

        logger.debug("Формируем json ответ")
        list_replacements = []
        
        result_date = await session.execute(db.select(db.table.Depends.date_replacements))
        date_replacements = result_date.scalar()
        
        for data_replace in results:
            for replace in data_replace:
                list_replacements.append({
                    "replace_id": replace.id,
                    "num_lesson": replace.num_lesson,
                    "item": replace.item,
                    "group": replace.group,
                    "cabinet": replace.cabinet,
                })
        
        output_json = {
            "teacher": teacher,
            "date": date_replacements,
            "replacements": list_replacements,
        }

        logger.debug("Формируем модель pydantic и вовзращаем")
        output_json_model = schemas.Replace_teacher_out(**output_json).model_dump()
        
        return output_json_model
    except Exception:
        logger.exception(f"Произошла ошибка при получении замен")
        return False





async def info_replace_by_id(
        replace_id: int, # example 21
        session: SessionDep # Сессия базы данных
) -> str | bool | schemas.Replace_full_info:
    try:
        logger.debug("Формируем запрос в бд")

        query_select = (
            db.select(db.table.Replacements)
            .filter_by(
                        id=replace_id,
                )
        )

        logger.debug("Выполняем запрос в бд")
        result = await session.execute(query_select)

        logger.debug("Получаем данные")
        result_data = result.first()
        
        if not result_data:
            logger.debug("Замена не найдена")
            return "Замена не найдена"
        
        
        logger.debug("Формируем json ответ")
        for replace in result_data:
            output_json = {
                "replace_id": replace.id,
                "num_lesson": replace.num_lesson,
                "item": replace.item,
                "group": replace.group,
                "cabinet": replace.cabinet,
                "teacher": replace.teacher
            }

        logger.debug("Формируем модель pydantic и вовзращаем")
        output_json_model = schemas.Replace_full_info(**output_json).model_dump()
        
        return output_json_model
    except Exception:
        logger.exception(f"Произошла ошибка при получении замен")
        return False




async def remove_replace(
        payload: schemas.Replace_remove,
        session: SessionDep # Сессия базы данных
) -> bool | str:
    try:
        logger.debug("Формируем запрос в бд")
        query_select = (
            db.select(db.table.Replacements)
            .filter_by(
                        group=payload.group,
                        num_day=schemas.Day_to_num[payload.day],
                        num_lesson=payload.num_lesson
                )
        )
        logger.debug("Выполняем запрос в бд")
        result = await session.execute(query_select)

        logger.debug("Получаем данные")
        replace_to_delete = result.scalar_one_or_none()

        if replace_to_delete:
            logger.debug("Замена найдена. Формируем запрос на удаление замены")
            query = (
                db.delete(db.table.Replacements)
                .filter(
                        db.table.Replacements.group == payload.group,
                        db.table.Replacements.num_day == schemas.Day_to_num[payload.day],
                        db.table.Replacements.num_lesson == payload.num_lesson,
                )
            )

            logger.debug("Выполняем запрос в бд")
            await session.execute(query)
            await session.commit()

            logger.debug("Замена успешно удалена. Возвращаем True")                    
            return True
        else:
            logger.debug("Замена не найдена. Возвращаем not found")
            return "not found"

    except Exception:
        logger.exception(f"При удалении произошла ошибка")
        return False
    
    


async def remove_replace_by_id(
        replace_id: int,
        session: SessionDep # Сессия базы данных
) -> bool:
    try:
        logger.debug("Формируем выполняем запрос в бд")
        await session.execute(db.delete(db.table.Replacements).filter_by(id=replace_id))

        await session.commit()

        logger.debug("Замена успешно удалена. Возвращаем True")                    
        return True
    except Exception:
        logger.exception(f"При удалении произошла ошибка")
        return False
    
    
async def remove_all_replacements(
    session: SessionDep
) -> bool:
    try:
        logger.debug("Формируем запрос в бд")
        query_delete = (
            db.delete(db.table.Replacements)
        )
        
        logger.debug("Выполняем запрос в бд")
        await session.execute(query_delete)
        await session.commit()
        
        logger.debug("Все замены успешно удалены. Возвращаем True")
        return True
    
    except Exception:
        logger.exception(f"При удалении всех замен произошла ошибка")
        return False