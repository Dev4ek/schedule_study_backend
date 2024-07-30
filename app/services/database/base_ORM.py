from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, validates, relationship
from sqlalchemy import ForeignKey, String, Boolean, Integer, ARRAY, JSON, SMALLINT


class Base(DeclarativeBase):
    pass


class Lessons(Base):
    __tablename__ = 'lesson'

    id: Mapped[Integer] = mapped_column(Integer, primary_key=True, autoincrement=True)
    num_day: Mapped[int] = mapped_column(SMALLINT())
    group: Mapped[String] = mapped_column(String(10), index=True)

    item: Mapped[str] = mapped_column(nullable=True)
    num_lesson: Mapped[int] = mapped_column(SMALLINT())
    
    week: Mapped[int] = mapped_column(SMALLINT())
    teacher: Mapped[String] = mapped_column(String(100), nullable=True)
    cabinet: Mapped[String] = mapped_column(String(50), nullable=True)


# class Replacements(Base):
#     __tablename__ ='replacement'

#     id: Mapped[Integer] = mapped_column(Integer, primary_key=True, autoincrement=True)
#     date: Mapped[str] = mapped_column(String(50))
#     num_day: Mapped[int] = mapped_column(SMALLINT())
#     group: Mapped[String] = mapped_column(String(10), index=True)

#     item: Mapped[str] = mapped_column(nullable=True)
#     num_lesson: Mapped[int] = mapped_column(SMALLINT())
    
#     week: Mapped[int] = mapped_column(SMALLINT())
#     teacher: Mapped[String] = mapped_column(String(100), nullable=True)
#     cabinet: Mapped[String] = mapped_column(String(50), nullable=True)


class Times(Base):
    __tablename__ = 'time'

    id: Mapped[Integer] = mapped_column(Integer, primary_key=True, autoincrement=True)
    num_day: Mapped[int] = mapped_column(SMALLINT())
    time: Mapped[String] = mapped_column(String(50))
    num_lesson: Mapped[int] = mapped_column(SMALLINT())


class Teachers(Base):
    __tablename__ = 'teacher'

    id: Mapped[Integer] = mapped_column(Integer, primary_key=True, autoincrement=True)
    full_name: Mapped[String] = mapped_column(String(100))
    short_name: Mapped[String] = mapped_column(String(50))

class Groups(Base):
    __tablename__ = 'group'

    id: Mapped[Integer] = mapped_column(Integer, primary_key=True, autoincrement=True)
    group: Mapped[String] = mapped_column(String(30))

class Cabinets(Base):
    __tablename__ = 'cabinet'

    id: Mapped[Integer] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cabinet: Mapped[String] = mapped_column(String(50))