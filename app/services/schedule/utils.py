from .. import database as db, rabbitmq
from loguru import logger

async def forming_schedule(group: str, reply_to) -> bool:
    logger.debug("processing schedule for group: {group}")

    async with db.get_session() as session:
        async with session.begin():
            query = (
                db.select(db.table.Schedule)
                .filter_by(group=group)
                .limit(1)
            )
            result = await session.execute(query)

            schedule = result.scalars().first()  # Получаем первый результат
        

            schedule = "ага"
            if schedule:
                await rabbitmq.response_in_queue(schedule, reply_to)
                return True


            return False
