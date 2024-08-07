from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
from typing_extensions import Annotated
from .time import Days


class Replace_input(BaseModel): 
    group: str = Field(...,  title="Группа", description="Группа у которой будет проходить пара", examples=["Испс-232", "Исп-211"])
    date: str = Field(..., title="Дата замен", description="На какое число и месяц будут установлены замены",  examples=["2 Сентября", "28 Января"])
    item: str = Field(...,  title="Предмет", description="Предмет который будет проходить", examples=["Математика", "Русский язык"])
    day: Days = Field(..., title="День недели", description="В какой день недели этот предмет будет проходить", examples=["Понедельник", "Вторник"])
    num_lesson: Annotated[int, Field(strict=True, ge=0, le=4, title="Номер пары", description="Номер пары, где 0-4, где - это классный час")]
    teacher: str = Field(...,  title="Учитель", description="Желательно полное ФИО учителя который будет преподавать пару", examples=["Лизенко Валерий Витальевич"])
    cabinet: str = Field(...,  title="Кабинет", description="Кабинет где будет проходить пара", examples=["405-1", "36-2"])


class Replace_remove(BaseModel):
    group: str = Field(...,  title="Группа", description="Группа у которой будет проходить пара", examples=["Испс-232", "Исп-211"])
    day: Days = Field(..., title="День недели", description="В какой день недели этот предмет будет проходить", examples=["Понедельник", "Вторник"])
    num_lesson: Annotated[int, Field(strict=True, ge=0, le=4, title="Номер пары", description="Номер пары, где 0-4, где - это классный час")]


class Replace_lesson(BaseModel):
    replace_id: int = Field(..., title="id в базе данных", examples=[43])
    item: str = Field(...,  title="Предмет", examples=["Математика", "Русский язык"])
    teacher: str = Field(...,  title="Учитель", description="Желательно полное ФИО учителя который будет преподаватьп пару", examples=["Демиденко Наталья Ильинична", "Лизенко Валерий Витальевич"])
    cabinet: str = Field(...,  title="Кабинет", description="Кабинет где будет проходить пара", examples=["405-1", "36-2"])
    day: Days = Field(..., title="День недели", description="В какой день недели этот предмет будет проходить", examples=["Понедельник", "Вторник"])
    num_lesson: Annotated[int, Field(strict=True, ge=0, le=4, title="Номер пары", description="Номер пары, где 0-4, где - это классный час")]


class Replace_output(BaseModel):
    group: str = Field(...,  title="Группа", examples=["Испс-232", "Исп-211"])
    date: str = Field(..., title="Дата", examples=["2 Сентября", "28 Января"])
    replacements: list[Replace_lesson] = Field(..., title="Информация о паре")
    
