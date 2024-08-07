from datetime import datetime, date, timedelta
import pytz
from loguru import logger
from app import schemas
from ..services import database as db
import calendar
from app.core.dependencies import SessionDep



# set timezone to Moscow
moscow_tz = pytz.timezone('Europe/Moscow')



async def set_time(
        payload: schemas.Put_time,
        session: SessionDep, # Сессия базы данных
) -> bool:  
    
    num_day = schemas.Day_to_num[payload.day]

    try:
        logger.debug(f"Формируем запрос в дб на проверку существующего времени на num_day: {num_day} и num_lesson {payload.num_lesson}")
        query_check = (
            db.select(db.table.Times.time)
            .where(db.and_(
                    db.table.Times.num_lesson==payload.num_lesson,
                    db.table.Times.num_day==num_day
                    )
                )   
            .limit(1)
        )

        logger.debug("Делаем запрос в бд")
        result = await session.execute(query_check)

        logger.debug("Получаем результат scalar_one_or_none")            
        existing_time = result.scalar_one_or_none()

        if existing_time:
            logger.debug("Время на такие параметры существует. Формируем запрос на его замену новым временем")
            query = (
                db.update(db.table.Times)
                    .where(db.and_(
                            db.table.Times.num_lesson==payload.num_lesson,
                            db.table.Times.num_day==num_day
                            )
                        ) 
                .values(time=payload.time)
            )

        else:
            logger.debug("Время в бд не найдено. Формируем запрос на добавление нового времени")
            query = (
                db.insert(db.table.Times)
                .values(
                    num_lesson=payload.num_lesson,
                    time=payload.time,
                    num_day=num_day
                    )
            )

        logger.success(f"Делаем запрос в бд")
        await session.execute(query)
        await session.commit()

        logger.debug("Время успешно установлено в бд. Возвращаем True")
        return True

    except Exception:
        logger.exception(f"при установке нового времени произошла ошибка")
        return False
    

async def get_day_and_week_number():
    try:
        
        logger.debug("Получаем today: datetime now дату и время")
        today = datetime.now(moscow_tz).date()

        logger.debug("Получаем num day сегодня. Понедельник - 1, Вторник - 2")
        num_day = calendar.weekday(today.year, today.month, today.day) + 1


        logger.debug("Получаем первый день месяца")
        first_day = date(today.year, today.month, 1)

        logger.debug("Вычисляем количество дней между первым днем месяца и заданной датой")
        days_since_start = (today - first_day).days

        logger.debug("Делим количество дней на 7 и округляем вверх, чтобы получить номер недели")
        week_number = (days_since_start // 7) + 1

        if week_number == 3 or week_number == 1:
            week_number = 1
        else:
            week_number = 2

        logger.debug("Успешно получили сегодняшний день и номер недели")
        return num_day, week_number

    except Exception:
        logger.exception(f"При получении сегодняшнего дня и номера недели произошла ошибка. Возвращаем None")
        return None
    



async def get_date_by_day(
        num_day: int # день недели Понедельник - 1, Вторник - 2
):
    try:
        logger.debug("Получаем today: datetime now дату и время")
        today = datetime.now(moscow_tz)

        logger.debug("Получем из текущего времени номер дня недели")
        current_weekday = today.weekday()

        logger.debug("Вычисляем количество дней до следующего целевого дня недели")
        days_until_target = (num_day - 1 - current_weekday + 7) % 7

        logger.debug("Создаем дату на следующий целевой день недели")
        next_date = today + timedelta(days=days_until_target)
        
        logger.debug("Переводим дату в понятную строку для пользователя")
        str_date = f"{next_date.day} {schemas.Num_to_month[next_date.month]}"

        logger.debug("Возвращаем эту строку")
        return str_date
    except Exception:
        logger.exception(f"При попытке получить дату на день денели произошла ошибка")
        return None

async def correct_str_minites(
        minutes: int
):

    logger.debug(f"correct_str_minites")

    try:
        minutes_last_symbol = str(minutes)[-1]


        if minutes == 11 or minutes == 12 or minutes == 13 or minutes == 14:
            return f"{minutes} минут"
        elif minutes_last_symbol == "1":
            return f"{minutes} минута"
        elif minutes_last_symbol == "2" or minutes_last_symbol == "3" or minutes_last_symbol == "4":
            return f"{minutes} минуты"
        else:
            return f"{minutes} минут"
    except Exception:
        logger.exception(f"ERROR correcting minutes")
        return None

async def check_time_lessons(event_time: list, previous_event_time: list):
    
    # Вложенная функция для расчета процента оставшегося времени
    async def check_percentage(total_seconds, elapsed_seconds):
        logger.debug("Вычисляем процент завершения")
        left_percentage = (elapsed_seconds / total_seconds) * 100
        logger.debug(f"Процент завершения: {left_percentage}%")
        return min(100, max(0, int(left_percentage)))

    try:
        logger.debug("Получаем текущее время")
        moscow_tz = pytz.timezone('Europe/Moscow')
        today = datetime.now(moscow_tz)
        current_time = datetime.strptime(f"{today.hour}:{today.minute}", "%H:%M")
        logger.debug(f"Текущее время: {current_time}")

        if not previous_event_time:
            logger.debug("Если нет предыдущего времени пары в аргументах, ставим на час назад")
            start_time_str_previous = event_time[0].split(" - ")[0]
            start_time_str_previous_time = datetime.strptime(start_time_str_previous, "%H:%M")
            logger.debug(f"Предыдущее время старта: {start_time_str_previous_time}")

            previous_event_time = [f"00:00 - {start_time_str_previous_time.hour - 1}:30"]
            logger.debug(f"Установлено предыдущее время пары: {previous_event_time}")

        for index, _event_time in enumerate(event_time):
            start_time_str, end_time_str = _event_time.split(" - ")
            logger.debug(f"Обработка события {index}: начало {start_time_str}, конец {end_time_str}")

            start_time = datetime.strptime(start_time_str, "%H:%M")
            end_time = datetime.strptime(end_time_str, "%H:%M")
            logger.debug(f"Время старта: {start_time}, Время окончания: {end_time}")

            if start_time <= current_time <= end_time:
                logger.debug("Текущее время находится в пределах текущего события")
                left_minutes = int((end_time - current_time).total_seconds() / 60)
                logger.debug(f"Оставшиеся минуты до конца события: {left_minutes}")
                correct_str_min = await correct_str_minites(left_minutes)

                total_seconds = (end_time - start_time).total_seconds()
                elapsed_seconds = (current_time - start_time).total_seconds()
                percentage = await check_percentage(total_seconds, elapsed_seconds)
                logger.debug(f"Процент завершения события: {percentage}")

                if index == len(event_time) - 1:
                    logger.debug("Текущая пара последняя в расписании")
                    return "active", f"До конца {correct_str_min}", percentage
                else:
                    logger.debug("Текущая пара не последняя, ожидается перерыв")
                    return "active", f"До перерыва {correct_str_min}", percentage
            elif current_time < start_time:
                logger.debug("Текущее время до начала следующего события")
                left_minutes = int((start_time - current_time).total_seconds() / 60)
                logger.debug(f"Оставшиеся минуты до начала следующего события: {left_minutes}")
                correct_str_min = await correct_str_minites(left_minutes)

                if index == 0:
                    logger.debug("Текущее время перед первым событием")
                    end_previous_lesson = previous_event_time[-1].split(" - ")[1]
                    end_previous_time = datetime.strptime(end_previous_lesson, "%H:%M")
                    logger.debug(f"Время окончания предыдущего события: {end_previous_time}")
                elif index == 1:
                    logger.debug("Текущее время перед вторым событием")
                    end_previous_lesson = event_time[0].split(" - ")[1]
                    end_previous_time = datetime.strptime(end_previous_lesson, "%H:%M")
                    logger.debug(f"Время окончания первого события: {end_previous_time}")

                total_seconds = (start_time - end_previous_time).total_seconds()
                elapsed_seconds = (current_time - end_previous_time).total_seconds()
                percentage = await check_percentage(total_seconds, elapsed_seconds)
                logger.debug(f"Процент завершения ожидания: {percentage}")

                if index == 0:
                    if left_minutes <= 60:
                        logger.debug("До начала следующего события меньше часа")
                        return "wait", f"До начала {correct_str_min}", percentage
                    logger.debug("До начала следующего события больше часа")
                    return "not active", "", 0
                else:
                    logger.debug("Ожидание продолжения после перерыва")
                    return "wait", f"До продолжения {correct_str_min}", percentage

        logger.debug("Ни одно из условий не выполнено, возвращаем None")
        return "not active", "", 0
    except Exception:
        logger.exception("Произошла ошибка в check_time_lessons")
        return "not active", "", 0

async def get_time(
        day: str, # Понедельник or None
        num_lesson: int, # 1, 2, 3, 4
        session: SessionDep
):
    try:
        num_day = schemas.Day_to_num[day] if day else None

        logger.debug("Формируем запрос на получение времени")
        query = (
            db.select(db.table.Times.num_day, 
                        db.table.Times.id, 
                        db.table.Times.num_lesson, 
                        db.table.Times.time)
            .order_by(
                    db.table.Times.num_day.asc(),
                    db.table.Times.num_lesson.asc()
            )
        )

        if num_day and num_lesson != None:
            logger.debug("Добавляем к запрос where num_day и num_lesson")
            query = query.where(db.and_(
                    db.table.Times.num_lesson==num_lesson,
                    db.table.Times.num_day==num_day
                    )
                )  
        elif num_day and num_lesson == None:
            logger.debug("Добавляем к запрос where num_day")
            query = query.where(
                    db.table.Times.num_day==num_day
                )  
        elif num_lesson != None and not num_day:
            logger.debug("Добавляем к запрос where num_lesson")
            query = query.where(
                    db.table.Times.num_lesson==num_lesson
                )   
        logger.debug("Делаем запрос в бд")
        result = await session.execute(query)

        logger.debug("Получаем данные")
        time = result.all()


        logger.debug("Преобразуем данные. Создаем словарь времени на каждый день")
        time_keys = []
        day_dict = {}
        for item in time:
            if item.num_day not in day_dict:
                day_dict[item.num_day] = []
            time_lesson_key = {
                "time_id": item.id,
                "num_lesson": item.num_lesson,
                "event_time": item.time,
            }
            day_dict[item.num_day].append(time_lesson_key)

        logger.debug("Преобразуем словарь в нужный формат списка")
        for num_day, lessons in day_dict.items():
            time_keys.append({
                "day": schemas.Num_to_day[num_day],
                "time": lessons
            })

        logger.debug("Возвращаем успешно сформированный json со временем")
        return time_keys
    except Exception:
        logger.exception(f"При получении времени произошла ошибка")
        return False



async def remove_time(
        payload: schemas.Remove_time,
        session: SessionDep
) -> bool | str:
    num_day = schemas.Day_to_num[payload.day]

    try:
        logger.debug(f"Формируем запрос на проверку времени в бд")
        check_time = (
            db.select(db.table.Times.time)
            .filter_by(
                num_lesson=payload.num_lesson,
                num_day=num_day
                )
            )
        logger.debug("Делаем запрос в бд")
        result = await session.execute(check_time)

        logger.debug("Получаем результат scalar_one_or_none")
        check = result.scalar_one_or_none()

        if check:
            logger.debug("Время в бд есть. Формируем запрос на удаление времени в бд")
            query = (
                db.delete(db.table.Times)
                .where(db.and_(
                        db.table.Times.num_lesson==payload.num_lesson,
                        db.table.Times.num_day==num_day
                        )
                    )
            )

            logger.debug("Делаем запрос в бд")
            await session.execute(query)
            await session.commit()

            logger.debug("Время успешно удалено. Возвращаем True")
            return True
        else:
            logger.debug("Время в бд не найдено. Возвращаем not found")
            return "not found"

    except Exception:
        logger.exception(f"Произошла ошибка при удалении времени")
        return False