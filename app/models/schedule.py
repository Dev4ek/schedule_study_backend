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
    cabinet: str
    week: Annotated[int, Field(strict=True, ge=0, le=2)]



class Lesson_in_db(BaseModel): 
    id: int
    num_day: int
    group: str
    item: str
    num_lesson: Annotated[int, Field(strict=True, ge=0, le=4, description="Номер пары")]
    event_time: list[str]
    week: Annotated[int, Field(strict=True, ge=1, le=2)]
    teacher: str
    cabinet: str


class Lesson_in_schedule(BaseModel):
    day: Optional[str] = None
    date: Optional[str] = None
    active: Optional[str] = None
    event_time: Optional[list[str]] = None
    time: Optional[str] = None


class Schedule_output(BaseModel):
    group: str = Field(..., description="Group number")
    week: Annotated[int, Field(strict=True, ge=1, le=2, description="Num week of schedule")]
    schedule: list[Lesson_in_schedule] = Field(..., description="List of lessons by days")


