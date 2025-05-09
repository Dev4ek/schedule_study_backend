from redis.asyncio import Redis
import os
from loguru import logger
import json
from typing import Any


async def check_lessons(key: str) -> dict | bool:
    try:
        logger.debug(f"Проверяем расписание в кеше redis. ключ: {key}")

        lessons_key = "lesssons:" + key
        
        logger.debug("Подключаемся к redis")
        redis = Redis.from_url(os.getenv('redis_url'),  decode_responses=True)
        
        logger.debug(f"Получаем информацию по ключу. Ключ: {lessons_key}")
        lessons = await redis.get(name=lessons_key)

        logger.debug("Закрываем соединение с redis")
        await redis.close()
    
        if lessons:
            logger.debug("Расписание есть в кеше redis. Возвращаем его")

            lessons_json = json.loads(lessons)
            return lessons_json
        
        else:
            logger.debug("Расписание не найдено в кеше redis. Возвращаем None")
            return None
        
    except Exception:
        logger.exception(f"Произошла ошибка при получании расписания из кеша. Группа: Исп-232")
        return None



async def set_lesssons(key: str, schedule: str) -> bool:
    try:
        logger.debug(f"Сохраняем расписание в кеше redis. ключ: {key}")
        lessons_key = "lesssons:" + key

        logger.debug("Подключаемся к redis")
        redis = Redis.from_url(os.getenv('redis_url'), encoding="utf8")

        lesssons_str = json.dumps(schedule)

        await redis.set(name=lessons_key, value=lesssons_str, ex=10)

        logger.debug("Расписание успешно установленно. Закрываем соединение с redis")
        await redis.close()

        logger.debug("Возвращаем True")
        return True
    except Exception:
        logger.exception(f"При установке расписания в кеш redis произошла ошибка. Группа: {key}")
        return False
    
    
    
    
    
    