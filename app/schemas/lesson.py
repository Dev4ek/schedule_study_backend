from typing import Optional
from pydantic import BaseModel, Field
from typing_extensions import Annotated
from .time import Days

class Check_setted_lessons_output(BaseModel):
    lesson_id: int = Field(..., title="id в базе данных", examples=[34])
    group: str = Field(...,  title="Группа", description="Группа у которой будет проходить пара", examples=["Исп-232", "Исп-211"])
    item: str = Field(...,  title="Предмет", description="Предмет который будет проходить", examples=["Математика", "Русский язык"])
    day: Days = Field(..., title="День недели", description="В какой день недели этот предмет будет проходить", examples=["Понедельник", "Вторник"])
    num_lesson: Annotated[int, Field(strict=True, ge=0, le=4, title="Номер пары", description="Номер пары, где 0-4, где - это классный час")]
    cabinet: str = Field(...,  title="Кабинет", description="Кабинет где будет проходить пара", examples=["405-1", "36-2"])
    week: Annotated[int, Field(strict=True, title="Неделя", description="Где 0 - это две недели сразу", ge=0, le=2)] # где 0 - это две недели сразу
    teacher: str = Field(...,  title="Учитель", description="Полное ФИО учителя который будет преподавать пару", examples=["Лизенко Валерий Витальевич"])
    

class Check_setted_output(BaseModel):
    use: bool = Field(..., title="Да Нет", description="True пара есть, False пары нет")
    lesson: Check_setted_lessons_output | None = Field(None, title="Пара", description="Если пара есть, то она присутствует здесь")

class Lesson_check_in(BaseModel):
    day: Days = Field(..., title="День недели", description="В какой день недели этот предмет будет проходить", examples=["Понедельник", "Вторник"])
    num_lesson: Annotated[int, Field(strict=True, ge=0, le=4, title="Номер пары", description="Номер пары, где 0-4, где - это классный час")]
    cabinet: str = Field(...,  title="Кабинет", description="Кабинет где будет проходить пара", examples=["405-1", "36-2"])
    week: Annotated[int, Field(strict=True, title="Неделя", description="Номер недели 1 или 2", ge=1, le=2)] # где 0 - это две недели сразу
    

class Lesson_input(BaseModel): 
    group: str = Field(...,  title="Группа", description="Группа у которой будет проходить пара", examples=["Исп-232", "Исп-211"])
    day: Days = Field(..., title="День недели", description="В какой день недели этот предмет будет проходить", examples=["Понедельник", "Вторник"])
    item: str = Field(...,  title="Предмет", description="Предмет который будет проходить", examples=["Математика", "Русский язык"])
    num_lesson: Annotated[int, Field(strict=True, ge=0, le=4, title="Номер пары", description="Номер пары, где 0-4, где - это классный час")]
    teacher: str = Field(...,  title="Учитель", description="Полное ФИО учителя который будет преподавать пару", examples=["Лизенко Валерий Витальевич"])
    cabinet: str = Field(...,  title="Кабинет", description="Кабинет где будет проходить пара", examples=["405-1", "36-2"])
    week: Annotated[int, Field(strict=True, title="Неделя", description="Где 0 - это две недели сразу", ge=0, le=2)] # где 0 - это две недели сразу

    
class Formed_replace_for_student(BaseModel):
    replace_id: int = Field(..., title="id в базе данных", examples=[34])
    item: str = Field(...,  title="Предмет", description="Предмет который будет проходить", examples=["Русский язык"])
    cabinet: str = Field(...,  title="Кабинет", description="Кабинет где будет проходить пара", examples=["405-1", "36-2"])
    teacher: str = Field(...,  title="Учитель", description="Полное ФИО учителя который будет преподавать пару", examples=["Лизенко Валерий Витальевич"])


class Formed_lesson_for_student_app(BaseModel):
    lesson_id: int = Field(..., title="id в базе данных", examples=[34])
    item: str = Field(...,  title="Предмет", description="Предмет который будет проходить", examples=["Математика", "Русский язык"])
    cabinet: str = Field(...,  title="Кабинет", description="Кабинет где будет проходить пара", examples=["405-1", "36-2"])
    teacher: str = Field(...,  title="Учитель", description="Полное ФИО учителя который будет преподавать пару", examples=["Лизенко Валерий Витальевич"])
    event_time: list[str] = Field(...,  title="Время проведения", examples=[ ["12:30 - 13:15","21:30 - 22:35"] ])
    num_lesson: Annotated[int, Field(strict=True, ge=0, le=4, description="Номер пары")]
    status: str  = Field(...,  title="Статус пары", description="Статус пары", examples=["not active", "wait", "active"])
    time: str = Field(...,  title="Текст времени", description="Инофрмация о выполнении пары", examples=["До начала 15 минут", "До про", "active"])
    percentage: int = Field(...,  title="Процент", description="Процент выполнения пары", examples=[89,21,9])
    replace: Formed_replace_for_student | None = Field(..., description="Замена пары")

class info_day_app(BaseModel):
    day: Days | str = Field(..., title="День", examples=["Понедельник", "Вторник"])
    date: str = Field(..., title="Дата", examples=["2 Сентября", "28 Января"])
    lessons: list[Formed_lesson_for_student_app] = Field(..., title="Список пар", description="Список пар на день")

class Schedule_app_output(BaseModel):
    group: str = Field(...,  title="Группа", description="Группа у которой будет проходить пара", examples=["Исп-232", "Исп-211"])
    week: Annotated[int, Field(strict=True, ge=1, le=2, description="Номер недели")]
    schedule: list[info_day_app] = Field(..., title="Список дней со списком пар", description="Список дней с парами")






class Formed_lesson_for_student(BaseModel):
    lesson_id: int = Field(..., title="id в базе данных", examples=[34])
    item: str = Field(...,  title="Предмет", description="Предмет который будет проходить", examples=["Математика", "Русский язык"])
    cabinet: str = Field(...,  title="Кабинет", description="Кабинет где будет проходить пара", examples=["405-1", "36-2"])
    teacher: str = Field(...,  title="Учитель", description="Полное ФИО учителя который будет преподавать пару", examples=["Лизенко Валерий Витальевич"])
    num_lesson: Annotated[int, Field(strict=True, ge=0, le=4, description="Номер пары")]
    replace: Formed_replace_for_student | None = Field(..., description="Замена пары")


class info_day(BaseModel):
    day: Days | str = Field(..., title="День", examples=["Понедельник", "Вторник"])
    date: str = Field(..., title="Дата", examples=["2 Сентября", "28 Января"])
    lessons: list[Formed_lesson_for_student] = Field(..., title="Список пар", description="Список пар на день")


class Schedule_output(BaseModel):
    group: str = Field(...,  title="Группа", description="Группа у которой будет проходить пара", examples=["Исп-232", "Исп-211"])
    week: Annotated[int, Field(strict=True, ge=1, le=2, description="Номер недели")]
    schedule: list[info_day] = Field(..., title="Список дней со списком пар", description="Список дней с парами")


class Remove_lesson(BaseModel):
    group: str = Field(...,  title="Группа", description="Группа у которой будет проходить пара", examples=["Исп-232", "Исп-211"])
    day: Days = Field(..., title="День", examples=["Понедельник", "Вторник"])
    num_lesson: Annotated[int, Field(strict=True, ge=0, le=4, description="Номер пары, где 0-4, где - это классный час")]
    week: Annotated[int, Field(strict=True, ge=0, le=2, description="Номер недели 0 - это 1 и 2 вместе")]
    
    
class Info_lesson_output(BaseModel):
    lesson_id: int = Field(..., title="id в базе данных", examples=[12])
    group: str = Field(...,  title="Группа", description="Группа у которой будет проходить пара", examples=["Исп-232", "Исп-211"])
    day: Days = Field(..., title="День", examples=["Понедельник", "Вторник"])
    num_lesson: Annotated[int, Field(strict=True, ge=0, le=4, description="Номер пары, где 0-4, где - это классный час")]
    item: str = Field(...,  title="Предмет", description="Предмет который будет проходить", examples=["Математика", "Русский язык"])
    teacher: str = Field(...,  title="Учитель", description="Полное ФИО учителя который будет преподавать пару", examples=["Лизенко Валерий Витальевич"])
    week: Annotated[int, Field(strict=True, ge=0, le=2, description="Номер недели 0 - это 1 и 2 вместе")]
    event_time: list[str] = Field(...,  title="Время проведения", examples=[ ["12:30 - 13:15","21:30 - 22:35"] ])
    replace: Formed_replace_for_student | None = Field(...,  description="Замена пары")