from datetime import datetime, time, date, timedelta
import json
import pytz
from loguru import logger

from app import models
from ..services import database as db
from icecream import ic
import calendar



# set timezone to Moscow
moscow_tz = pytz.timezone('Europe/Moscow')



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

                logger.success(f"Set time successfully")
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

        logger.success("successfully get day and week number")
        return num_day, week_number


    except Exception:
        logger.exception(f"ERROR getting week number")
        return None
    



async def get_date_by_day(
        num_day
):
    logger.debug(f"get_date_by_day")

    try:
        today = datetime.now(moscow_tz)

        current_weekday = today.weekday()

        # Вычисляем количество дней до следующего целевого дня недели
        days_until_target = (num_day - 1 - current_weekday + 7) % 7

        next_date = today + timedelta(days=days_until_target)
        
        str_date = f"{next_date.day} {models.Num_month[next_date.month]}"

        logger.success(f"getting date by day successfully")
        return str_date
    except Exception:
        logger.exception(f"ERROR getting date by day")
        return None

async def correct_str_minites(
        minutes: int
):

    logger.debug(f"correct_str_minites")

    try:
        minutes_last_symbol = str(minutes)[-1]

        if minutes_last_symbol == "1":
            return f"{minutes} минута"
        elif minutes == 11 or minutes == 12 or minutes == 13 or minutes == 14:
            return f"{minutes} минут"

        elif minutes_last_symbol == "2" or minutes_last_symbol == "3" or minutes_last_symbol == "4":
            return f"{minutes} минуты"
        else:
            return f"{minutes} минут"
    except Exception:
        logger.exception(f"ERROR correcting minutes")
        return None

async def check_time_lessons(
        event_time: list
):
    try:
        today = datetime.now(moscow_tz)

        current_time = datetime.strptime(f"{today.hour}:{today.minute}", "%H:%M")

        for index, _event_time in enumerate(event_time):
            start_time_str, end_time_str = _event_time.split(" - ")

            start_time = datetime.strptime(start_time_str, "%H:%M")
            end_time = datetime.strptime(end_time_str, "%H:%M")

            if start_time <= current_time <= end_time:
                left_minutes = int((end_time - current_time).total_seconds() / 60)
                correct_str_min = await correct_str_minites(left_minutes)

                if index == len(event_time) - 1:
                    return "active", f"До конца {correct_str_min}"
                else:
                    return "active", f"До перерыва {correct_str_min}"

            elif current_time < start_time:
                left_minutes = int((start_time - current_time).total_seconds() / 60)
                correct_str_min = await correct_str_minites(left_minutes)

                if index == 0:
                    if left_minutes < 120:
                        return "wait", f"До начала {correct_str_min}"
                    return None, ""

                else:
                    return "wait", f"До продолжения {correct_str_min}"

        return None, ""
    except Exception:        
        logger.exception("error check_time_lessons")
        return None, ""


async def get_time(
        day,
        num_lesson
):
    try:
        if day:
            num_day = models.Day_num[day]
        else:
            num_day = None

                
        async with await db.get_session() as session:
            async with session.begin():
                query = (
                    db.select(db.table.Times.num_day, 
                              db.table.Times.num_lesson, 
                              db.table.Times.time)
                    .order_by(
                            db.table.Times.num_day.asc(),
                            db.table.Times.num_lesson.asc()
                    )
                )

                if num_day and num_lesson:
                    query = query.where(db.and_(
                            db.table.Times.num_lesson==num_lesson,
                            db.table.Times.num_day==num_day
                            )
                        )  
                elif num_day and not num_lesson:
                    query = query.where(
                            db.table.Times.num_day==num_day
                        )  
                elif not num_day and num_lesson:
                    query = query.where(
                            db.table.Times.num_lesson==num_lesson
                        )   

                result = await session.execute(query)
                time = result.all()

                time_keys = []

                # create a dictionary for each day with time
                day_dict = {}
                for item in time:
                    if item.num_day not in day_dict:
                        day_dict[item.num_day] = []
                    time_lesson_key = {
                        "num_lesson": item.num_lesson,
                        "event_time": item.time,
                    }
                    day_dict[item.num_day].append(time_lesson_key)

                # convert dictionary to the desired list format
                for num_day, lessons in day_dict.items():
                    time_keys.append({
                        "day": models.Num_day[num_day],
                        "num_day": num_day,
                        "time": lessons
                    })

                return time_keys
    except Exception:
        logger.exception(f"ERROR getting time for num_lesson : {num_lesson}, day: {day}")
        return False



async def remove_time(
        num_day: int, # Понедельник - 1 , Вторник - 2
        num_lesson: int, # number lesson example 1 or 2 or 3...
):
    
    logger.debug(f"Removing time , day: {num_day}, num_lesson: {num_lesson}")

    try:
        async with await db.get_session() as session:
            async with session.begin():
                check_time = (
                    db.select(db.table.Times.time)
                    .filter_by(
                        num_lesson=num_lesson,
                        num_day=num_day
                        )
                    )
                result = await session.execute(check_time)

                check = result.scalar_one_or_none()

                if check:
                    query = (
                        db.delete(db.table.Times)
                       .where(db.and_(
                                db.table.Times.num_lesson==num_lesson,
                                db.table.Times.num_day==num_day
                                )
                            )
                    )

                    await session.execute(query)
                    return True


                else:
                    return "not found"

    except Exception:
        logger.exception(f"ERROR getting time for num_lesson : {num_lesson}, day: {num_day}")
        return False