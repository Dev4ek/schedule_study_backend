from typing import Optional
from pydantic import BaseModel, Field
from typing_extensions import Annotated
from .time import Days


class Lesson_input(BaseModel): 
    group: str = Field(...,  title="Группа", examples=["Испс-232", "Исп-211"])
    day: Days = Field(..., title="День", examples=["Понедельник", "Вторник"])
    item: str = Field(...,  title="Предмет", examples=["Математика", "Русский язык"])
    num_lesson: Annotated[int, Field(strict=True, ge=0, le=4, description="Номер пары, где 0-4, где - это классный час")]
    teacher: str = Field(...,  title="Учитель", examples=["Демиденко Наталья Ильинична", "Лизенко Валерий Витальевич"])
    cabinet: str = Field(...,  title="Кабинет", examples=["405-1", "36-2"])
    week: Annotated[int, Field(strict=True, ge=0, le=2)] # где 0 - это две недели сразу


class Formed_replace(BaseModel):
    item: str = Field(...,  title="Предмет", examples=["Математика", "Русский язык"])
    teacher: str = Field(...,  title="Учитель", examples=["Демиденко Наталья Ильинична", "Лизенко Валерий Витальевич"])
    cabinet: str = Field(...,  title="Кабинет", examples=["405-1", "36-2"])

class Formed_lesson(BaseModel):
    item: str = Field(...,  title="Предмет", examples=["Математика", "Русский язык"])
    cabinet: str = Field(...,  title="Кабинет", examples=["405-1", "36-2"])
    teacher: str = Field(...,  title="Учитель", examples=["Демиденко Наталья Ильинична", "Лизенко Валерий Витальевич"])
    event_time: list[str] = Field(...,  title="Время проведения", examples=[ ["12:30 - 13:15","21:30 - 22:35"] ])
    num_lesson: Annotated[int, Field(strict=True, ge=0, le=4, description="Номер пары")]
    status: str = Field(...,  title="Статус пары", examples=["None", "wait", "active"])
    time: str = Field(...,  title="Текст времени", examples=["До начала 15 минут", "До про", "active"])
    percentage: str = Field(...,  title="Процент", description="Процент выполнения пары", examples=[89,21,9])
    replace: list[Formed_replace] | None = Field(..., description="Замена пары")

class info_day(BaseModel):
    day: Days = Field(..., title="День", examples=["Понедельник", "Вторник"])
    date: str = Field(..., title="Дата", examples=["2 Сентября", "28 Января"])
    lessons: list[Formed_lesson] = Field(..., description="Список занятий на день")


class Schedule_output(BaseModel):
    group: str = Field(...,  title="Группа", examples=["Испс-232", "Исп-211"])
    week: Annotated[int, Field(strict=True, ge=1, le=2, description="Номер недели")]
    schedule: list[info_day] = Field(..., description="Список дней с парами")


class Remove_lesson(BaseModel):
    group: str = Field(...,  title="Группа", examples=["Испс-232", "Исп-211"])
    day: Days = Field(..., title="День", examples=["Понедельник", "Вторник"])
    num_lesson: Annotated[int, Field(strict=True, ge=0, le=4, description="Номер пары, где 0-4, где - это классный час")]
    week: Annotated[int, Field(strict=True, ge=0, le=2, description="Номер недели 0 - это 1 и 2 вместе")]