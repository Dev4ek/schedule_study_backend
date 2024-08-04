from typing import Optional
from pydantic import BaseModel, Field
from typing_extensions import Annotated
from .time import Days


class Account_input(BaseModel): 
    loggin: str
    password: str