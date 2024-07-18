from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, validates
from sqlalchemy import ForeignKey, String, Boolean, Integer, ARRAY, JSON
from typing import Optional, List
from sqlalchemy.ext.declarative import declarative_base


class Base(DeclarativeBase):
    pass


class Schedule(Base):
    __tablename__ ='schedule'

    id: Mapped[Integer] = mapped_column(Integer, primary_key=True, autoincrement=True)
    group: Mapped[String] = mapped_column(String(10), index=True)
    schedule: Mapped[List[JSON]] = mapped_column(ARRAY(JSON))
    


