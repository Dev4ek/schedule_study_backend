from enum import Enum
from pydantic import BaseModel, Field
from typing import Annotated

Day_to_num = {
    "Понедельник": 1,
    "Вторник": 2,
    "Среда": 3,
    "Четверг": 4,
    "Пятница": 5,
    "Суббота": 6,
    "Воскресенье": 7,
}

Num_to_day = {
    1: "Понедельник",
    2: "Вторник",
    3: "Среда",
    4: "Четверг",
    5: "Пятница",
    6: "Суббота",
    7: "Воскресенье",
}

Num_to_month = {
    1: "Января",
    2: "Февраля",
    3: "Марта",
    4: "Апреля",
    5: "Мая",
    6: "Июня",
    7: "Июля",
    8: "Августа",
    9: "Сентября",
    10: "Октября",
    11: "Ноября",
    12: "Декабря"

}


class Days(str, Enum):
    Понедельник = "Понедельник"
    Вторник = "Вторник"
    Среда = "Среда"
    Четверг = "Четверг"
    Пятница = "Пятница"
    Суббота = "Суббота"
    Воскресенье = "Воскресенье"


class Put_time(BaseModel):
    day: Days = Field(..., title="День", examples=["Понедельник", "Вторник"])
    num_lesson: Annotated[int, Field(strict=True, ge=0, le=4, description="Номер пары, где 0-4, где - это классный час")]
    time: str = Field(..., description="Время для пары", example="8:30 - 9:15, 9:15 - 10:00")

class Remove_time(BaseModel):
    day: Days = Field(..., title="День", examples=["Понедельник", "Вторник"])
    num_lesson: Annotated[int, Field(strict=True, ge=0, le=4, description="Номер пары, где 0-4, где - это классный час")]