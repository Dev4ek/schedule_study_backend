import asyncio
import json
import aio_pika
from aio_pika.abc import AbstractIncomingMessage
import os
from icecream import ic
from loguru import logger


async def send_in_queue_schedule(
        group: str
) -> str:
    connection = None
    try:
        logger.debug(f"send request in queue rabbit. {group}")

        connection: aio_pika.RobustConnection = await aio_pika.connect_robust(
            os.getenv('rabbitmq_url')
        )

        routing_key = "queue_schedule"
        channel = await connection.channel()
        temp_queue = await channel.declare_queue(exclusive=True, auto_delete=True)

        response = asyncio.Future()

        # consume response from queue schedule
        async def callback(message: aio_pika.IncomingMessage) -> None:
            if not response.done():
                response.set_result(message.body.decode())
                logger.debug(f"Received response from queue")  

        await temp_queue.consume(callback)

        # publish message to queue schedule 
        await channel.default_exchange.publish(
            aio_pika.Message(
                body=group.encode(),
                reply_to=temp_queue.name
            ),
            routing_key=routing_key
        )

        logger.debug("Message published to queue")  

        result = await response

    except Exception:
        logger.exception(f"CRITICAL ERROR send request in queue rabbit: {group}")
        result = None

    finally:
        if connection:
            await connection.close()

    return result



async def response_in_queue_schedule(
        schedule: str, # schedule which need send to rabbitmq
        reply_to: AbstractIncomingMessage # name temp queue which send response
) -> bool:
    try:
        logger.debug(f"send response rabbit to queue {reply_to}.") 
        
        connection: aio_pika.RobustConnection = await aio_pika.connect_robust(
            os.getenv('rabbitmq_url')
        )

        channel = await connection.channel()

        await channel.default_exchange.publish(
            aio_pika.Message(
                body=schedule.encode(),
            ),
            routing_key=reply_to
        )

        logger.debug(f"Response sent to queue {reply_to}")

    except Exception:
        logger.exception(f"ERROR send response schedule rabbit")
        return False

    finally:
        if connection:
            await connection.close()
