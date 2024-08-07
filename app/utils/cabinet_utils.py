from ..services import database as db
from app.core.dependencies import SessionDep
from loguru import logger

async def all_cabinets(session: SessionDep) -> dict | bool:
    try:
        logger.debug("Формирование запроса для бд")
        query = (
            db.select(db.table.Cabinets.id, db.table.Cabinets.cabinet)
            .order_by(db.table.Cabinets.cabinet.asc())
        )

        logger.debug("Выполняем запрос в бд")
        result = await session.execute(query)

        logger.debug("Получаем результат из бд")
        cabients_data = result.all()

        cabients = []
        for cabinet in cabients_data:
            cabients.append({
                "cabinet_id": cabinet.id,
                "cabinet": cabinet.cabinet
                 })

        
        logger.debug("Формируем json список кабинетов для ответа")
        return cabients

    except Exception:
        logger.exception(f"Произошла ошибка при получении списка кабинето")
        return False
    


async def put_cabinet(
        cabinet: str, # example: "405-1"
        session: SessionDep # Сессия базы данных
) -> bool | str:
    try:
        logger.debug("Формируем запрос для проверки кабинета в бд")
        query_check = (
            db.select(db.table.Cabinets.cabinet)
            .where(db.table.Cabinets.cabinet == cabinet)
        )

        logger.debug("Выполняем запрос в бд")
        result = await session.execute(query_check)

        logger.debug("Получаем данные")
        exists_cabinet = result.scalar_one_or_none()


        if exists_cabinet:
            logger.debug("Кабинет уже существует, ничего не делаем и отдаем ответ exists")
            return "exists"

        else:
            logger.debug("Кабинет в бд не найден. Формируем запрос на добавлении кабинета в бд")
            query = (
                db.insert(db.table.Cabinets)
                .values(cabinet=cabinet)
            )

        logger.debug("Выполняем запрос в бд")
        await session.execute(query)
        await session.commit()

        logger.debug("Кабинет успешно добавлен в бд")
        return True

    except Exception:
        logger.exception(f"При добавлении кабинета в бд произошла ошибка")
        return False
    
async def remove_cabinet(
        cabinet: str, # example: "405-1"б
        session: SessionDep # Сессия базы данных
) -> bool | str:
    try:
        logger.debug("Формируем запрос для проверки кабинета в бд")
        query_check = (
            db.select(db.table.Cabinets.cabinet)
            .where(db.table.Cabinets.cabinet == cabinet)
        )

        logger.debug("Выполняем запрос в бд")
        result = await session.execute(query_check)

        logger.debug("Получаем результат scalar_one_or_none")
        exists_cabinet = result.scalar_one_or_none()

        if exists_cabinet:
            logger.debug("Кабинет существует. Формируем запрос для его удаления")
            query = (
                db.delete(db.table.Cabinets)
                .where(db.table.Cabinets.cabinet == cabinet)
            )
            logger.debug("Выполняем запрос в бд")
            await session.execute(query)
            await session.commit()
            
            logger.debug("Кабинет успешно удалён из бд")
            return True
        else:
            logger.debug(f"Кабинет не найден в бд, возвращаем not found")
            return "not found"

    except Exception:
        logger.exception(f"Произошла ошибка при удалении кабинета из базы данных")
        return False
