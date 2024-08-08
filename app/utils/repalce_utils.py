from ..services import database as db
from loguru import logger
from .. import schemas
from app import schemas
from app.core.dependencies import SessionDep
from icecream import ic


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
                        date=payload.date,
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
                        date=payload.date,
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
                    date=payload.date,
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



async def all_replacemetns(
        session: SessionDep # Сессия базы данных
) -> schemas.Replacements_all_out | bool:
    try:
        logger.debug("Формируем запросы в бд")
        query_select = (
            db.select(db.table.Replacements)
            .order_by(db.table.Replacements.group, db.table.Replacements.num_day, db.table.Replacements.num_lesson)
        )

        logger.debug("Выполняем запросы в бд")
        result = await session.execute(query_select)
        result_date = await session.execute(db.select(db.table.Depends.date_replacements))

        logger.debug("Получаем данные")
        results = result.all()

        date_replacements = result_date.scalar()

        logger.debug("Формируем json ответ")
        
        output_json = {
            "date": date_replacements,
            "data": []
        }
        
        for data_replace in results:
            list_replacements = []
            
            for replace in data_replace:
                repalce_info = {
                    "replace_id": replace.id,
                    "num_lesson": replace.num_lesson,
                    "item": replace.item,
                    "teacher": replace.teacher,
                    "cabinet": replace.cabinet,
                }

                adding = False
                
                for i in output_json["data"]:
                    if i["group"] == replace.group:
                        i["replacements"].append(repalce_info)
                        adding = True
                if not adding:
                    list_replacements.append(repalce_info)
                    output_json["data"].append({
                            "group": replace.group,
                            "replacements": list_replacements
                        })  


        ic(output_json)
        logger.debug("Формируем pydantic модель и возвращаем ответ")
        all_replacemetns_model_out = schemas.Replacements_all_out(**output_json).model_dump()

        return all_replacemetns_model_out
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