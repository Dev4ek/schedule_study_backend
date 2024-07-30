from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
from typing_extensions import Annotated
from .time import Days


class Cabinet_input(BaseModel):
    cabinet: str = Field(..., description="Кабинет")