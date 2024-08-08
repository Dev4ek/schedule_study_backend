from typing import Optional
from pydantic import BaseModel, Field
from typing_extensions import Annotated
from .time import Days



class Formed_replace_for_teacher(BaseModel):
    replace_id: int = Field(..., title="id в базе данных", examples=[34])
    item: str = Field(...,  title="Предмет", description="Предмет который будет проходить", examples=["Математика", "Русский язык"])
    cabinet: str = Field(...,  title="Кабинет", description="Кабинет где будет проходить пара", examples=["405-1", "36-2"])
    group: str = Field(...,  title="Группа", description="Группа у которой будет проходить пара", examples=["Исп-232", "Исп-211"])



class Formed_lesson_for_teacher_app(BaseModel):
    lesson_id: int = Field(..., title="id в базе данных", examples=[34])
    group: str = Field(...,  title="Группа", description="Группа у которой будет проходить пара", examples=["Исп-232", "Исп-211"])
    item: str = Field(...,  title="Предмет", description="Предмет который будет проходить", examples=["Математика", "Русский язык"])
    cabinet: str = Field(...,  title="Кабинет", description="Кабинет где будет проходить пара", examples=["405-1", "36-2"])
    event_time: list[str] = Field(...,  title="Время проведения", examples=[ ["12:30 - 13:15","21:30 - 22:35"] ])
    num_lesson: Annotated[int, Field(strict=True, ge=0, le=4, description="Номер пары")]
    status: str  = Field(...,  title="Статус пары", description="Статус пары", examples=["not active", "wait", "active"])
    time: str = Field(...,  title="Текст времени", description="Инофрмация о выполнении пары", examples=["До начала 15 минут", "До про", "active"])
    percentage: int = Field(...,  title="Процент", description="Процент выполнения пары", examples=[89,21,9])
    replace: Formed_replace_for_teacher | None = Field(..., description="Замена пары")


class Formed_lesson_for_teacher(BaseModel):
    lesson_id: int = Field(..., title="id в базе данных", examples=[34])
    group: str = Field(...,  title="Группа", description="Группа у которой будет проходить пара", examples=["Исп-232", "Исп-211"])
    item: str = Field(...,  title="Предмет", description="Предмет который будет проходить", examples=["Математика", "Русский язык"])
    cabinet: str = Field(...,  title="Кабинет", description="Кабинет где будет проходить пара", examples=["405-1", "36-2"])
    replace: Formed_replace_for_teacher | None = Field(..., description="Замена пары")



class info_day(BaseModel):
    day: Days = Field(..., title="День", examples=["Понедельник", "Вторник"])
    date: str = Field(..., title="Дата", examples=["2 Сентября", "28 Января"])
    lessons: list[Formed_lesson_for_teacher_app] | list[Formed_lesson_for_teacher] = Field(..., title="Список пар", description="Список пар на день")

    
class Schedule_tacher_output(BaseModel):
    teacher: str = Field(...,  title="Учитель", description="Учитель который будет проводить пару", examples=["Демиденко Натьалья Ильинична"])
    week: Annotated[int, Field(strict=True, ge=1, le=2, description="Номер недели")]
    schedule: list[info_day] = Field(..., title="Список дней со списком пар", description="Список дней с парами")
