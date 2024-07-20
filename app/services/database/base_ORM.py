from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, validates, relationship
from sqlalchemy import ForeignKey, String, Boolean, Integer, ARRAY, JSON, SMALLINT


class Base(DeclarativeBase):
    pass


class Schedule(Base):
    __tablename__ = 'schedule'

    id: Mapped[Integer] = mapped_column(Integer, primary_key=True, autoincrement=True)
    group: Mapped[String] = mapped_column(String(10), index=True)
    schedule: Mapped[str] = mapped_column()
    num_lesson: Mapped[int] = mapped_column(SMALLINT(), ForeignKey("time.num_lesson"))
    
    time: Mapped["Time"] = relationship("Time", back_populates="num_lesson")




class Time(Base):
    __tablename__ = 'time'

    id: Mapped[Integer] = mapped_column(Integer, primary_key=True, autoincrement=True)
    day: Mapped[String] = mapped_column(String(30))
    time: Mapped[String] = mapped_column(String(50))
    num_lesson: Mapped[int] = mapped_column(SMALLINT(), unique=True)

    schedule: Mapped["Schedule"] = relationship("Schedule", back_populates="num_lesson")

    


    
    