from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
from typing_extensions import Annotated
from .time import Days


class Lesson_input(BaseModel): 
    group: str
    day: Days
    item: str
    num_lesson: Annotated[int, Field(strict=True, ge=0, le=4, description="Номер пары")]
    teacher: str
    auditory: str
    week: Annotated[int, Field(strict=True, ge=1, le=2)]



class Lesson_in_db(BaseModel): 
    id: int
    num_day: int
    group: str
    item: str
    num_lesson: Annotated[int, Field(strict=True, ge=0, le=4, description="Номер пары")]
    event_time: list[str]
    week: Annotated[int, Field(strict=True, ge=1, le=2)]
    teacher: str
    auditory: str


class Lesson_in_schedule(BaseModel):
    day: Optional[str] = None
    date: Optional[str] = None
    active: Optional[bool] = None
    event_time: Optional[list[str]] = None
    time: Optional[str] = None


class Form_schedule(BaseModel):
    group: Optional[str] = None
    week: Optional[str] = None
    schedule: Optional[Lesson_in_schedule] = None



