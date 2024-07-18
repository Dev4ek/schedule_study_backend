import asyncio
import aio_pika
import aio_pika.abc
import os
from icecream import ic
from loguru import logger


async def send_in_queue(group: str) -> str:
    try:
        logger.debug(f"send request in queue rabbit. {group}")
        
        connection: aio_pika.RobustConnection = await aio_pika.connect_robust(
            os.getenv('rabbitmq_url')
        )

        routing_key = "queue_schedule"
        channel = await connection.channel()
        temp_queue = await channel.declare_queue(exclusive=True, auto_delete=True)

        response = asyncio.Future()

        async def callback(message: aio_pika.IncomingMessage) -> None:
            response.set_result(message.body.decode())

        await temp_queue.consume(callback)

        await channel.default_exchange.publish(
            aio_pika.Message(
                body=group.encode(),
                reply_to=temp_queue.name
            ),
            routing_key=routing_key
        )

        result = await response
    except Exception as e:
        logger.exception(f"CRITICAL ERROR send request in queue rabbit: {group}")
        result = None

    finally:
        await connection.close()


    return result



async def response_in_queue(body, reply_to) -> bool:
    try:
        logger.debug(f"send response rabbit.")
        
        connection: aio_pika.RobustConnection = await aio_pika.connect_robust(
            os.getenv('rabbitmq_url')
        )

        channel = await connection.channel()

        await channel.default_exchange.publish(
            aio_pika.Message(
                body=body.encode(),
            ),
            routing_key=reply_to
        )

    except Exception as e:
        logger.exception(f"ERROR send response  schedule rabbit")
        return False

    finally:
        await connection.close()