from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
from typing_extensions import Annotated
from .time import Days


class Replace_input(BaseModel): 
    group: str = Field(...,  title="Группа", examples=["Испс-232", "Исп-211"])
    date: str = Field(..., title="Дата", examples=["2 Сентября", "28 Января"])
    item: str = Field(...,  title="Предмет", examples=["Математика", "Русский язык"])
    day: Days = Field(..., title="День", examples=["Понедельник", "Вторник"])
    num_lesson: Annotated[int, Field(strict=True, ge=0, le=4, description="Номер пары")]
    teacher: str = Field(...,  title="Учитель", examples=["Демиденко Наталья Ильинична", "Лизенко Валерий Витальевич"])
    cabinet: str = Field(...,  title="Кабинет", examples=["405-1", "36-2"])


class Replace_remove(BaseModel):
    group: str = Field(...,  title="Группа", examples=["Испс-232", "Исп-211"])
    day: Days = Field(..., title="День", examples=["Понедельник", "Вторник"])
    num_lesson: Annotated[int, Field(strict=True, ge=0, le=4, description="Номер пары")]


class Replace_lesson(BaseModel):
    id: int = Field(..., title="id в базе данных", examples=[34])
    item: str = Field(...,  title="Предмет", examples=["Математика", "Русский язык"])
    teacher: str = Field(...,  title="Учитель", examples=["Демиденко Наталья Ильинична", "Лизенко Валерий Витальевич"])
    cabinet: str = Field(...,  title="Кабинет", examples=["405-1", "36-2"])
    day: Days = Field(..., title="День", examples=["Понедельник", "Вторник"])
    num_lesson: Annotated[int, Field(strict=True, ge=0, le=4, description="Номер пары")]


class Replace_output(BaseModel):
    group: str = Field(...,  title="Группа", examples=["Испс-232", "Исп-211"])
    date: str = Field(..., title="Дата", examples=["2 Сентября", "28 Января"])
    replacements: list[Replace_lesson] = Field(..., title="Информация о паре")