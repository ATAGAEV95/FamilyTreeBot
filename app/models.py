from sqlalchemy import CheckConstraint, Column, Date, ForeignKey, Integer, String, Text
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from config import DATABASE_URL, SCHEMA


def get_engine(schema: str) -> create_async_engine:
    """Создает и возвращает асинхронный движок SQLAlchemy с указанной схемой."""
    return create_async_engine(
        DATABASE_URL, connect_args={"server_settings": {"search_path": schema}}
    )


if SCHEMA is None or SCHEMA == "":
    engine = get_engine("public")
else:
    engine = get_engine(SCHEMA)
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    """Базовый класс для всех моделей, поддерживающий асинхронные атрибуты."""

    pass


class Persons(Base):
    """Модель таблицы 'persons' для хранения информации о людях."""

    __tablename__ = "persons"

    person_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50))
    father_name = Column(String(50))
    birth_date = Column(Date)
    death_date = Column(Date)
    gender = Column(String(10), CheckConstraint("gender IN ('Мужской', 'Женский')"))
    bio = Column(Text)
    photo_url = Column(String(255))


class Relationship(Base):
    """Модель таблицы 'relationships' для хранения родственных связей между людьми."""

    __tablename__ = "relationships"

    relationship_id = Column(Integer, primary_key=True, autoincrement=True)
    parent_id = Column(Integer, ForeignKey("persons.person_id"), nullable=False)
    child_id = Column(Integer, ForeignKey("persons.person_id"), nullable=False)
    relationship_type = Column(
        String(20),
        CheckConstraint("relationship_type IN ('Родной', 'Приемный', 'Отчим', 'Мачеха')"),
    )

    __table_args__ = (CheckConstraint("parent_id <> child_id"),)


class Marriage(Base):
    """Модель таблицы 'marriages' для хранения информации о браках."""

    __tablename__ = "marriages"

    marriage_id = Column(Integer, primary_key=True, autoincrement=True)
    husband_id = Column(Integer, ForeignKey("persons.person_id"), nullable=False)
    wife_id = Column(Integer, ForeignKey("persons.person_id"), nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)


class Users(Base):
    """Модель таблицы 'users' для хранения информации о пользователях.

    Также нужен для проверки доступа пользователя к боту.
    """

    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, autoincrement=False)
    username = Column(String)


async def init_models() -> None:
    """Создает таблицы в базе данных, если они не существуют."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
