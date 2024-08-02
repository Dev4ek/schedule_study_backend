import json
from ..services import database as db
from loguru import logger
from aio_pika.abc import AbstractIncomingMessage
import asyncio
from . import time_utils
from .. import schemas
from icecream import ic
import pydantic
from app import schemas


async def put_replace(
        replace: schemas.Replace_input, # example: "Демиденко Наталья Ильинична"
):
    logger.debug("start adding replace")

    try:
        # Open session to database
        async with await db.get_session() as session:
            async with session.begin():

                #checking replace in db
                query_check = (
                    db.select(db.table.Replacements.id)
                   .filter_by(
                              group=replace.group,
                              date=replace.date,
                              num_day=schemas.Day_num[replace.day],
                              num_lesson=replace.num_lesson,
                        )
                )

                result = await session.execute(query_check)
                exists_replace = result.scalar_one_or_none()


                if exists_replace:
                    query = (
                        db.update(
                            db.table.Replacements
                        )
                        .values(
                            item=replace.item,
                            teacher=replace.teacher,
                            cabinet=replace.cabinet,
                        )
                        .filter_by(
                              group=replace.group,
                              date=replace.date,
                              num_day=schemas.Day_num[replace.day],
                              num_lesson=replace.num_lesson,
                        )
                    )

                else:
                    get_date_query = db.select(db.table.Replacements.date).limit(1)
                    result = await session.execute(get_date_query)
                    last_date = result.scalar_one_or_none()


                    # if not last_date == replace.date:
                    #     return "not date"

                    query = (
                        db.insert(db.table.Replacements)
                        .values(
                            group=replace.group,
                            date=replace.date,
                            num_day=schemas.Day_num[replace.day],
                            num_lesson=replace.num_lesson,
                            item=replace.item,
                            teacher=replace.teacher,
                            cabinet=replace.cabinet,
                        )
                    )

                await session.execute(query)
                return True

    except Exception:
        logger.exception(f"ERROR adding replace to database")
        return False
    




async def all_replacemetns(
        group: str # example "Исп-232"
):
    logger.debug(f"start selet replacemetns for group {group}")

    try:
        # Open session to database
        async with await db.get_session() as session:
            async with session.begin():

                query_select = (
                    db.select(db.table.Replacements)
                   .filter_by(
                              group=group,
                        )
                )

                result = await session.execute(query_select)
                results = result.scalars().all()

                date_replacemetns = None
                list_replacemetns = []


                for replace in results:
                    date_replacemetns = replace.date
                    list_replacemetns.append(
                        {
                            "id": replace.id,
                            "item": replace.item,
                            "teacher": replace.teacher,
                            "cabinet": replace.cabinet,
                            "day": schemas.Num_day[replace.num_day],
                            "lesson_num": replace.num_lesson,
                        }
                    )

                output_json = {
                    "group": group,
                    "date": date_replacemetns,
                    "replacemetns": list_replacemetns,
                }
                return output_json
    except Exception:
        logger.exception(f"ERROR getting replacemetns from database")
        return False

     


async def remove_replace(replace: schemas.Replace_remove):
    logger.debug(f"start remove remove")

    try:
        # Open session to database
        async with await db.get_session() as session:
            async with session.begin():

                query_select = (
                    db.select(db.table.Replacements)
                   .filter_by(
                              group=replace.group,
                              num_day=schemas.Day_num[replace.day],
                              num_lesson=replace.num_lesson
                        )
                )

                result = await session.execute(query_select)
                replace_to_delete = result.scalar_one_or_none()

                if replace_to_delete:
                    query = (
                        db.delete(db.table.Replacements)
                       .filter(
                                db.table.Replacements.group == replace.group,
                                db.table.Replacements.num_day == schemas.Day_num[replace.day],
                                db.table.Replacements.num_lesson == replace.num_lesson,
                        )
                    )

                    await session.execute(query)
                    return True
                else:
                    return "not found"

    except Exception:
        logger.exception(f"ERROR remove replace from database")
        return False