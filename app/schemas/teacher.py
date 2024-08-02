from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
from typing_extensions import Annotated
from .time import Days


class Teacher_input(BaseModel):
    full_name: str = Field(..., description="ФИО учителя")