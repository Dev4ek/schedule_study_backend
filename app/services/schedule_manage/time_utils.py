from datetime import datetime, time
import pytz
from loguru import logger

# set timezone to Moscow
moscow_tz = pytz.timezone('Europe/Moscow')

async def timing_couples(schedule: dict) -> dict:
    time_now = datetime.now(moscow_tz).time()

    for event_time in schedule[0]['event_time']:

        time_start_str = event_time.split(' - ')[0]

        if time_now < time.fromisoformat(time_start_str):
            ...
        else:
            schedule[0]['time'] = f"{time_start_str} - {event_time.split(' - ')[1]}"
            break



async def set_time(day: str, start: str, end: str, text: str, para: str) -> bool:
    # set timezone to Moscow
    moscow_tz = pytz.timezone('Europe/Moscow')

    time_start = datetime.strptime(start, '%H:%M').time()
    time_end = datetime.strptime(end, '%H:%M').time()

    # check time range
    if time_start >= time_end:
        logger.error(f"Invalid time range: {start} - {end}")
        return False

    schedule = {
        'day': day,
        'start': start,
        'end': end,
        'text': text,
        'para': para
    }

    return schedule