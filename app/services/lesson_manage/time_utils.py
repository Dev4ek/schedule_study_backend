from datetime import datetime, time, date, timedelta
import pytz
from loguru import logger

from app import models
from .. import database as db
from icecream import ic
import calendar



# set timezone to Moscow
moscow_tz = pytz.timezone('Europe/Moscow')

async def timing_couples(schedule: dict) -> dict:

    ...
    ...
    ...
    
    
    # time_now = datetime.now(moscow_tz).time()

    # for event_time in schedule[0]['event_time']:

    #     time_start_str = event_time.split(' - ')[0]

    #     if time_now < time.fromisoformat(time_start_str):
    #         ...
    #     else:
    #         schedule[0]['time'] = f"{time_start_str} - {event_time.split(' - ')[1]}"
    #         break



async def set_time(
        num_day: int, # day example Понедельник - 1, Воскресенье - 7 ...
        num_lesson: int, # number lesson example 1 or 2 or 3...
        time: dict 
) -> bool:  
    logger.debug("set time")

    try:
        # open session to database
        async with await db.get_session() as session:
            async with session.begin():

                # form qery to get schedule from database
                query_check = (
                    db.select(db.table.Times.time)
                    .where(db.and_(
                            db.table.Times.num_lesson==num_lesson,
                            db.table.Times.num_day==num_day
                            )
                        )   
                    .limit(1)
                )

                # checking time existence in database
                result = await session.execute(query_check)

                existing_time = result.scalar_one_or_none()

                if existing_time:
                    
                    query = (
                        db.update(db.table.Times)
                         .where(db.and_(
                                    db.table.Times.num_lesson==num_lesson,
                                    db.table.Times.num_day==num_day
                                    )
                                ) 
                        .values(time=time)
                    )

                else:
                    query = (
                        db.insert(db.table.Times)
                        .values(
                            num_lesson=num_lesson,
                            time=time,
                            num_day=num_day
                            )
                    )

                await session.execute(query)
                return True


    except Exception:
        logger.exception(f"ERROR set time for num_lesso : {num_lesson}, time: {time}")
        return False
    

async def get_day_and_week_number():
    logger.debug("get_week_number")

    try:
      
        today = datetime.now(moscow_tz).date()

        num_day = calendar.weekday(today.year, today.month, today.day) + 1

        first_day = date(today.year, today.month, 1)

        # Вычисляем количество дней между первым днем месяца и заданной датой
        days_since_start = (today - first_day).days

        # Делим количество дней на 7 и округляем вверх, чтобы получить номер недели
        week_number = (days_since_start // 7) + 1

        if week_number == 3 or week_number == 1:
            week_number = 1
        else:
            week_number = 2


        return num_day, week_number


    except Exception:
        logger.exception(f"ERROR getting week number")
        return None
    



async def get_date_by_day(num_day):
    today = datetime.now(moscow_tz)

    current_weekday = today.weekday()

    # Вычисляем количество дней до следующего целевого дня недели
    days_until_target = (num_day - 1 - current_weekday + 7) % 7

    next_date = today + timedelta(days=days_until_target)
    
    str_date = f"{next_date.day} {models.Num_month[next_date.month]}"

    return str_date
    
