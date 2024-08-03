from ..services import database as db
from loguru import logger
from app.core.dependencies import SessionDep


async def all_groups(
    session: SessionDep, # Сессия базы данных
) -> dict:
    try:
        logger.debug("Формируем запрос на получение всех групп")
        query = (
            db.select(db.table.Groups.group)
        )

        logger.debug("Выполняем запрос")
        result = await session.execute(query)

        logger.debug("Получаем результат")
        groups = result.scalars().all()

        logger.debug("Формируем json список групп для ответа")
        return {
            "groups": groups
        }

    except Exception:
        logger.exception(f"Произошла ошибка при получении всех групп")
        return False


async def put_group(
        group: str, # example: "Исп-232"
        session: SessionDep # Сессия базы данных
) -> bool | str:
    try:
        logger.debug("Формируем запрос на проверку наличие группы в бд")
        query_check = (
            db.select(db.table.Groups.group)
            .where(db.table.Groups.group == group)
        )

        logger.debug("Выполняем запрос в бд")
        result = await session.execute(query_check)

        logger.debug("Получаем результат scalar_one_or_none")
        exists_group = result.scalar_one_or_none()

        if exists_group:
            logger.debug("Группа существует. Вовзращаем exists")
            return "exists"

        else:
            logger.debug("Группа не существует. Формируем запрос в бд")
            query = (
                db.insert(db.table.Groups)
                .values(group=group)
            )

        logger.debug("Выполняем запрос в бд")
        await session.execute(query)
        await session.commit()

        logger.debug("Группа успешно добавлена. Возвращаем True")
        return True

    except Exception:
        logger.exception(f"Произошла ошибка при добавлении группы в бд")
        return False
    

async def remove_group(
        group: str, # example: "Исп-232"
        session: SessionDep, # Сессия базы данных

) -> bool | str:
    try:
        logger.debug("Формируем запрос на проверку группы в бд")
        query_check = (
            db.select(db.table.Groups.group)
            .where(db.table.Groups.group == group)
        )

        logger.debug("Выполняем запрос в бд")
        result = await session.execute(query_check)

        logger.debug("Получаем результат scalar_one_or_none")
        exists_group = result.scalar_one_or_none()

        if exists_group:
            logger.debug("Группа существует. Формируем запрос на удаление группы из бд")
            query = (
                db.delete(db.table.Groups)
                .where(db.table.Groups.group == group)
            )

            logger.debug("Выполняем запрос в бд")
            await session.execute(query)
            await session.commit()

            logger.debug("Группа успешно удалена из бд. Возвращаем True")
            return True
        else:
            logger.debug(f"Группа не существует в бд. Возвращаем not found")
            return "not found"

    except Exception:
        logger.exception(f"ERROR remove group from database")
        return False
