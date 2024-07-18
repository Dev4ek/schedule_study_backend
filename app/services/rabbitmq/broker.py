import os
import aio_pika
import asyncio
from icecream import ic
from loguru import logger
from . import utils
from asyncio import Semaphore
from app.services.schedule import utils

from app.core import config
sem = Semaphore(config.count_threads)


async def start_schedule():
    connection = await aio_pika.connect_robust(
        os.getenv('rabbitmq_url')
    )
    try:
        async with connection:
            queue_name = "queue_schedule"

            channel = await connection.channel()

            queue = await channel.declare_queue(
                queue_name,
                auto_delete=True
            )

            await channel.set_qos(config.count_threads)

            logger.info("RabbitMQ connected and waiting")

            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with sem:
                        asyncio.create_task(utils.forming_schedule(message.body.decode(), reply_to=message.reply_to))


            await asyncio.Future()

    except Exception as e:
        logger.exception(f"Error RabbitMQ: {e}")




