from dotenv import load_dotenv, find_dotenv
import asyncio
from loguru import logger
import datetime


dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

from app.services import database
from app.core import main

# config logs
logger.add(f'logs/{datetime.datetime.now()}.log', rotation="3:00", level="DEBUG")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def running():
        await asyncio.gather(
            database.core.create_tables(),
            main.start(),
        )


    loop.run_until_complete(running())
    loop.close()