from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, validates, relationship
from sqlalchemy import ForeignKey, String, Boolean, Integer, ARRAY, JSON, SMALLINT


class Base(DeclarativeBase):
    pass



class Schedule(Base):
    __tablename__ = 'schedule'

    id: Mapped[Integer] = mapped_column(Integer, primary_key=True, autoincrement=True)
    num_day: Mapped[int] = mapped_column(SMALLINT())
    group: Mapped[String] = mapped_column(String(10), index=True)
    schedule: Mapped[str] = mapped_column()

    today: Mapped[Boolean] = mapped_column(Boolean)
    tomorrow: Mapped[Boolean] = mapped_column(Boolean)

    time_0: Mapped[str] = mapped_column(String(50), nullable=True)
    time_1: Mapped[str] = mapped_column(String(50), nullable=True)
    time_2: Mapped[str] = mapped_column(String(50), nullable=True)
    time_3: Mapped[str] = mapped_column(String(50), nullable=True)
    time_4: Mapped[str] = mapped_column(String(50), nullable=True)



class Time(Base):
    __tablename__ = 'time'

    id: Mapped[Integer] = mapped_column(Integer, primary_key=True, autoincrement=True)
    num_day: Mapped[int] = mapped_column(SMALLINT())
    time: Mapped[String] = mapped_column(String(50))
    num_lesson: Mapped[int] = mapped_column(SMALLINT())

