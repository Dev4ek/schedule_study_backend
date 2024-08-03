from ..services import database as db
from loguru import logger
from app.core.dependencies import SessionDep


async def all_teachers(
        session: SessionDep
) -> dict | bool:
    try:
        logger.debug("Формируем запрос в бд")
        query = (
            db.select(db.table.Teachers.full_name)
        )

        logger.debug("Выполняем запрос в бд")
        result = await session.execute(query)

        logger.debug("Получаем данные из бд")
        teachers = result.scalars().all()
        
        logger.debug("Вовзращаем json учителей")
        return {
            "teachers": teachers
        }
    except Exception:
        logger.exception(f"Произошла ошибка при получении списка учителей")
        return False
    


async def put_teacher(
        full_name: str, # example: "Демиденко Наталья Ильинична"
        session: SessionDep
) -> bool | str:
    
    try:
        logger.debug("Формируем запрос на проверку наличия учителя в бд")        
        query_check = (
            db.select(db.table.Teachers.full_name)
            .where(db.table.Teachers.full_name == full_name)
        )
        logger.debug("Делаем запрос в бд")
        result = await session.execute(query_check)

        logger.debug("Получаем результат scalar_one_or_none")
        exists_teacher = result.scalar_one_or_none()

        if exists_teacher:
            logger.debug("Учитель существует. Возвращаем exists")
            return "exists"

        else:
            logger.debug("Учителя не существует. Формируем запрос на добавление учителя в бд")
            query = (
                db.insert(db.table.Teachers)
                .values(full_name=full_name, short_name=full_name)
            )

        logger.debug("Делаем запрос в бд")
        await session.execute(query)
        await session.commit()

        logger.debug("Учитель успешно добавлен в бд. Возвращаем True")
        return True

    except Exception:
        logger.exception(f"При добавлении учителя произошла ошибка")
        return False
    


    
async def remove_teacher(
        full_name: str, # example: "Демиденко Наталья Ильинична"
        session: SessionDep
) -> bool | str:
    try:
        logger.debug("Формируем запрос в бд на проверку учителя в бд")
        query_check = (
            db.select(db.table.Teachers.full_name)
            .where(db.table.Teachers.full_name == full_name)
        )
        logger.debug("Выполняем запрос в бд")
        result = await session.execute(query_check)

        logger.debug("Получаем результат scalar_one_or_none")
        exists_teacher = result.scalar_one_or_none()

        if exists_teacher:
            logger.debug("Учитель есть в бд. Формируем запрос на удаление")
            query = (
                db.delete(db.table.Teachers)
                .where(db.table.Teachers.full_name == full_name)
            )

            logger.debug("Выполняем запрос в бд")
            await session.execute(query)
            await session.commit()

            logger.debug("Учитель успешно удалён из бд. Возвращаем True")
            return True
        else:
            logger.debug(f"Учитель не найден в бд. Вовзаращаем not found")
            return "not found"


    except Exception:
        logger.exception(f"Произошла ошибка при встаке учителя в бд")
        return False
