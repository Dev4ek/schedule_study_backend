from dotenv import load_dotenv, find_dotenv
import asyncio
from loguru import logger
import datetime

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

from app.services import database
from app.core import fastapi
from app.services import rabbitmq

# config logs
logger.add(f'logs/{datetime.datetime.now()}.log', rotation="3:00", level="DEBUG")

if __name__ == "__main__":

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def main():
        await asyncio.gather(
            database.core.create_tables(),
            fastapi.start(),
            rabbitmq.start_schedule()
        )


    loop.run_until_complete(main())
    loop.close()