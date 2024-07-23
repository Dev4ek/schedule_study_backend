import os
import aio_pika
import asyncio
from icecream import ic
from loguru import logger
from . import utils
from .. import lesson_manage

from app.core import config

async def process_message(message):
    try:
        # start getting schedule from database
        await lesson_manage.get_lessons(group=message.body.decode(), reply_to=message.reply_to)

        await message.ack()
    except Exception:
        logger.exception(f"Error processing message")
        await message.nack(requeue=False)  # Optionally nack the message if processing fails



async def start_schedule():
    try:
        connection = await aio_pika.connect_robust(os.getenv('rabbitmq_url'))
    except Exception:
        logger.exception(f"Error connecting to RabbitMQ")
        return False

    try:
        async with connection:
            queue_name = "queue_schedule"
            channel = await connection.channel()

            # Create queue for schedule
            queue = await channel.declare_queue(queue_name, auto_delete=True)

            # Set max queue simultaneous streams
            await channel.set_qos(config.max_queue)

            logger.info("RabbitMQ connected and waiting")

            # Consume messages from queue
            async with queue.iterator() as queue_iter:
                tasks = []
                async for message in queue_iter:
                    task = asyncio.create_task(process_message(message))
                    tasks.append(task)
                    
                    tasks = [t for t in tasks if not t.done()]
                
                # Wait for all remaining tasks to complete
                await asyncio.gather(*tasks)
    except Exception:
        logger.exception(f"Error in RabbitMQ connection handling")
