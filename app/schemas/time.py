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


class Put_time_out(BaseModel):
    time_id: int = Field(..., title="id", description="id в базе данных", examples=[3])

class Put_time(BaseModel):
    day: Days = Field(..., title="День", examples=["Понедельник", "Вторник"])
    num_lesson: Annotated[int, Field(strict=True, ge=0, le=4, description="Номер пары, где 0-4, где - это классный час")]
    time: str = Field(..., description="Время для пары", example="8:30 - 9:15, 9:15 - 10:00")

class Remove_time(BaseModel):
    day: Days = Field(..., title="День", examples=["Понедельник", "Вторник"])
    num_lesson: Annotated[int, Field(strict=True, ge=0, le=4, description="Номер пары, где 0-4, где - это классный час")]
    
    
class Info_time(BaseModel):
    time_id: int = Field(..., title="id в базе данных", examples=[3])
    num_lesson: Annotated[int, Field(strict=True, ge=0, le=4, description="Номер пары, где 0-4, где - это классный час")]
    event_time: list[str] = Field(...,  title="Время проведения", description="Время когда будет проходить пара", examples=[ ["12:30 - 13:15","21:30 - 22:35"] ])
        
class Info_day_time(BaseModel):
    day: Days = Field(..., title="День",description="День проведения пары", examples=["Понедельник", "Вторник"])
    time: list[Info_time] = Field(..., title="Информация о времени", description="Информация когда будет проходить пара")

class Check_time(BaseModel):
    time: list[Info_day_time] = Field(..., title="Информация о времени", description="Информация о времени по дням и номер парам")
    
    
class Week_Day(BaseModel):
    day: Days = Field(..., title="День", description="День недели", examples=["Понедельник", "Вторник"])
    week: Annotated[int, Field(strict=True, title="Неделя", description="Номер текущей недели", ge=1, le=2)] # где 0 - это две недели сразу