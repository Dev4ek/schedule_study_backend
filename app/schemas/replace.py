from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
from typing_extensions import Annotated
from .time import Days


class Replace_in(BaseModel): 
    group: str = Field(...,  title="Группа", description="Группа у которой будет проходить пара", examples=["Исп-232", "Исп-211"])
    date: str = Field(..., title="Дата замен", description="Дата замен когда их добавили", examples=["2 Сентября", "28 Января"])
    item: str = Field(...,  title="Предмет", description="Предмет который будет проходить", examples=["Математика", "Русский язык"])
    day: Days = Field(..., title="День недели", description="В какой день недели этот предмет будет проходить", examples=["Понедельник", "Вторник"])
    num_lesson: Annotated[int, Field(strict=True, ge=0, le=4, title="Номер пары", description="Номер пары, где 0-4, где - это классный час")]
    teacher: str = Field(...,  title="Учитель", description="Полное ФИО учителя который будет преподавать пару", examples=["Лизенко Валерий Витальевич"])
    cabinet: str = Field(...,  title="Кабинет", description="Кабинет где будет проходить пара", examples=["405-1", "36-2"])


class Replace_remove(BaseModel):
    group: str = Field(...,  title="Группа", description="Группа у которой будет проходить пара", examples=["Исп-232", "Исп-211"])
    date: str = Field(..., title="Дата замен", description="Дата замен когда их добавили", examples=["2 Сентября", "28 Января"])
    day: Days = Field(..., title="День недели", description="В какой день недели этот предмет будет проходить", examples=["Понедельник", "Вторник"])
    num_lesson: Annotated[int, Field(strict=True, ge=0, le=4, title="Номер пары", description="Номер пары, где 0-4, где - это классный час")]


class Replace_lesson(BaseModel):
    replace_id: int = Field(..., title="id в базе данных", examples=[43])
    item: str = Field(...,  title="Предмет", examples=["Математика", "Русский язык"])
    num_lesson: Annotated[int, Field(strict=True, ge=0, le=4, title="Номер пары", description="Номер пары, где 0-4, где - это классный час")]
    cabinet: str = Field(...,  title="Кабинет", description="Кабинет где будет проходить пара", examples=["405-1", "36-2"])
    teacher: str = Field(...,  title="Учитель", description="Полное ФИО учителя который будет преподавать пару", examples=["Демиденко Наталья Ильинична", "Лизенко Валерий Витальевич"])


class Replace_out(BaseModel):
    group: str = Field(...,  title="Группа", examples=["Исп-232", "Исп-211"])
    date: str = Field(..., title="Дата", examples=["2 Сентября", "28 Января"])
    replacements: list[Replace_lesson] = Field(..., title="Информация о заменах", description="Информация о заменах")

class Replacement_data(BaseModel):
    group: str = Field(..., title="Группа", description="Группа у которой будет проходить пара", examples=["Исп-232", "Исп-211"])
    replacements: list[Replace_lesson] = Field(..., title="Информация о паре")

class Replacements_all_out(BaseModel):
    date: str = Field(..., title="Дата замен", description="Дата замен когда их добавили", examples=["2 Сентября", "28 Января"])
    data: list[Replacement_data] = Field(..., title="Информация", description="Информация о заменах с группами")
    
class Replace_full_info(BaseModel):
    replace_id: int = Field(..., title="id в базе данных", examples=[43])
    date: str = Field(..., title="Дата замен", description="Дата замен когда их добавили", examples=["2 Сентября", "28 Января"])
    item: str = Field(...,  title="Предмет", examples=["Математика", "Русский язык"])
    num_lesson: Annotated[int, Field(strict=True, ge=0, le=4, title="Номер пары", description="Номер пары, где 0-4, где - это классный час", examples=[2])]
    cabinet: str = Field(...,  title="Кабинет", description="Кабинет где будет проходить пара", examples=["405-1", "36-2"])
    teacher: str = Field(...,  title="Учитель", description="Полное ФИО учителя который будет преподавать пару", examples=["Демиденко Наталья Ильинична", "Лизенко Валерий Витальевич"])
    group: str = Field(...,  title="Группа", examples=["Исп-232", "Исп-211"])



class Replace_check(BaseModel):
    use: bool = Field(..., title="True or False", description="true - замена есть, false - замены нет")
    replace: Replace_full_info | None = Field(..., title="Инфо о замене", description="Полная инфомрация о замене")
    
    
class Replace_id(BaseModel):
    replace_id: int = Field(..., title="id в базе данных", examples=[43])