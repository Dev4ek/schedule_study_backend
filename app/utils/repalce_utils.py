from ..services import database as db
from loguru import logger
from .. import schemas
from app import schemas
from app.core.dependencies import SessionDep



async def put_replace(
        payload: schemas.Replace_input,
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
) -> schemas.Replace_output | bool:
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
        results = result.scalars().all()

        date_replacemetns = None
        list_replacemetns = []

        logger.debug("Формируем json ответ")
        for replace in results:
            date_replacemetns = replace.date
            list_replacemetns.append(
                {
                    "id": replace.id,
                    "item": replace.item,
                    "teacher": replace.teacher,
                    "cabinet": replace.cabinet,
                    "day": schemas.Num_to_day[replace.num_day],
                    "num_lesson": replace.num_lesson,
                }
            )

        output_json = {
            "group": group,
            "date": date_replacemetns,
            "replacemetns": list_replacemetns,
        }

        logger.debug("Возвращаем json ответ")
        return output_json
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