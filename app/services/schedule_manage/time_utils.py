from datetime import datetime, time
import pytz
from loguru import logger
from .. import database as db
from icecream import ic



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
                    db.select(db.table.Time.time)
                    .where(db.and_(
                            db.table.Time.num_lesson==num_lesson,
                            db.table.Time.num_day==num_day
                            )
                        )   
                    .limit(1)
                )

                # checking time existence in database
                result = await session.execute(query_check)

                existing_time = result.scalar_one_or_none()

                if existing_time:
                    
                    query = (
                        db.update(db.table.Time)
                         .where(db.and_(
                                    db.table.Time.num_lesson==num_lesson,
                                    db.table.Time.num_day==num_day
                                    )
                                ) 
                        .values(time=time)
                    )

                else:
                    query = (
                        db.insert(db.table.Time)
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
    


async def time_for_lessons(num_day) -> dict:
    logger.debug("time_for_lessons day: {num_day}")

    time_dict = {
                "time_0": None,
                "time_1": None,
                "time_2": None,
                "time_3": None,
                "time_4": None,
             }


    try:
        # open session to database
        async with await db.get_session() as session:
            async with session.begin():

                # get time lessons
                query_time_lessons = (
                    db.select(db.table.Time.time, db.table.Time.num_lesson)
                    .filter_by(num_day=num_day)
                )
                

                # execute query to database and get time lessons as list of tuples
                time_lessons_object = await session.execute(query_time_lessons)
                time_lessons = time_lessons_object.all()

                # fill time_dict with time lessons
                for time_data in time_lessons:
                    num = time_data[1]
                    time = time_data[0]

                    time_dict[f"time_{num}"] = time

    except Exception:
        logger.exception(f"ERROR getting time lessons from database")
        
    return time_dict