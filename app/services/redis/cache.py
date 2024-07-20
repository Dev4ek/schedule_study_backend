from redis.asyncio import Redis
import os
from loguru import logger



async def check_schedule(group):
    try:
        shedule_key = "schedule:" + group
        
        logger.debug(f"Checking schedule in cache redis: key: {shedule_key}")

        # connect to redis
        redis = Redis.from_url(os.getenv('redis_url'))
        
        # get schedule from redis
        schedule = await redis.get(name=shedule_key)

        await redis.close()
    
        return schedule.decode() if schedule else None
    except Exception as e:
        logger.exception(f"ERROR checking schedule in cache redis: key {group}")
        return None



async def set_schedule(group, schedule):
    try:
        shedule_key = "schedule:" + group

        logger.debug(f"set schedule cache redis: key: {shedule_key}")

        # encoding schedule to bytes for redis
        encoding_schedule = schedule.encode()

        # connect to redis
        redis = Redis.from_url(os.getenv('redis_url'))

        # set schedule to redis with expire time 15 seconds (optional)
        await redis.set(name=shedule_key, value=encoding_schedule, ex=15)

        await redis.close()

        return True
    except Exception as e:
        logger.exception(f"ERROR set schedule in cache redis: key {group}")
        return False