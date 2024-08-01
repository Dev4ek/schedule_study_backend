from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
from typing_extensions import Annotated
from .time import Days


class Replace_input(BaseModel): 
    group: str
    date: str
    item: str
    day: Days
    num_lesson: Annotated[int, Field(strict=True, ge=0, le=4, description="Номер пары")]
    teacher: str
    cabinet: str


class Replace_remove(BaseModel):
    group: str
    day: Days
    num_lesson: Annotated[int, Field(strict=True, ge=0, le=4, description="Номер пары")]