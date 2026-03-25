import asyncio
from typing import Sequence

from sqlalchemy import and_, case, or_, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import aliased

from app.models import Marriage, Persons, Relationship, Users, async_session

DB_TIMEOUT = 10


async def get_person(person_id: int) -> Persons | None:
    """Извлекает данные персоны по её ID."""
    try:
        async with async_session() as session:
            query = select(Persons).where(Persons.person_id == person_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()
    except Exception as e:
        print(f"Ошибка получения персонажа: {e}")
        return None


async def get_siblings(first_name: str, last_name: str) -> list[dict]:
    """Возвращает список братьев и сестёр по имени и фамилии."""
    try:
        async with async_session() as session:
            target_person = await session.execute(
                select(Persons.person_id).where(
                    and_(
                        Persons.first_name == first_name, Persons.last_name == last_name
                    )
                )
            )
            target_id = target_person.scalar()
            if not target_id:
                return []
            subquery = select(Relationship.parent_id).where(
                Relationship.child_id == target_id
            )
            stmt = (
                select(
                    Persons.first_name,
                    Persons.last_name,
                    Persons.father_name,
                    case((Persons.gender == "Мужской", "Брат"), else_="Сестра").label(
                        "sibling_type"
                    ),
                )
                .select_from(Persons)
                .join(Relationship, Relationship.child_id == Persons.person_id)
                .where(
                    and_(
                        Relationship.parent_id.in_(subquery),
                        Persons.person_id != target_id,
                    )
                )
                .distinct()
            )
            result = await session.execute(stmt)
            return [dict(row._mapping) for row in result.all()]
    except Exception as e:
        print(f"Ошибка при получении братьев/сестер: {e}")
        return []


async def get_parents(child_first_name: str, child_last_name: str) -> list[dict]:
    """Возвращает список родителей по имени и фамилии ребёнка."""
    try:
        async with async_session() as session:
            Child = aliased(Persons)
            Parent = aliased(Persons)

            query = (
                select(
                    Parent.first_name,
                    Parent.last_name,
                    Parent.father_name,
                )
                .select_from(Relationship)
                .join(Parent, Relationship.parent_id == Parent.person_id)
                .join(Child, Relationship.child_id == Child.person_id)
                .where(
                    and_(
                        Child.first_name == child_first_name,
                        Child.last_name == child_last_name,
                    )
                )
            )
            result = await session.execute(query)
            return [dict(row._mapping) for row in result.all()]
    except Exception as e:
        print(f"Ошибка при получении родителей: {e}")
        return []


async def search_persons(search_str: str) -> Sequence[Persons] | list[Persons]:
    """Ищет людей по имени и/или фамилии."""
    try:
        async with async_session() as session:
            search_str = search_str.strip()
            search_terms = search_str.split()
            query = select(Persons)
            conditions = []
            if len(search_terms) == 2:
                term1, term2 = search_terms
                conditions.extend(
                    [
                        and_(
                            Persons.first_name.ilike(f"%{term1}%"),
                            Persons.last_name.ilike(f"%{term2}%"),
                        ),
                        and_(
                            Persons.first_name.ilike(f"%{term2}%"),
                            Persons.last_name.ilike(f"%{term1}%"),
                        ),
                    ]
                )
            else:
                term = search_str
                conditions.extend(
                    [
                        Persons.last_name.ilike(f"%{term}%"),
                        Persons.first_name.ilike(f"%{term}%"),
                    ]
                )
            query = query.where(or_(*conditions))
            result = await session.execute(query)
            return result.scalars().all()
    except Exception as e:
        print(f"Ошибка поиска: {e}")
        return []


async def get_spouses(first_name: str, last_name: str) -> list[dict]:
    """Возвращает список супругов по имени и фамилии."""
    try:
        async with async_session() as session:
            target_subq = (
                select(Persons.person_id)
                .where(
                    and_(
                        Persons.first_name == first_name, Persons.last_name == last_name
                    )
                )
                .scalar_subquery()
            )
            spouse_type = case(
                (Persons.gender == "Мужской", "Супруг"), else_="Супруга"
            ).label("spouse_type")
            query = (
                select(
                    Persons.first_name,
                    Persons.last_name,
                    Persons.father_name,
                    spouse_type,
                )
                .join(
                    Marriage,
                    or_(
                        Persons.person_id == Marriage.husband_id,
                        Persons.person_id == Marriage.wife_id,
                    ),
                )
                .where(
                    Persons.person_id != target_subq,
                    or_(
                        Marriage.wife_id == target_subq,
                        Marriage.husband_id == target_subq,
                    ),
                )
            )
            result = await session.execute(query)
            return [dict(row._mapping) for row in result.all()]
    except Exception as e:
        print(f"Ошибка при получении супруга: {e}")
        return []


async def get_children(first_name: str, last_name: str) -> list[dict]:
    """Возвращает список детей по имени и фамилии родителя."""
    try:
        async with async_session() as session:
            parent_query = select(Persons.person_id).where(
                and_(Persons.first_name == first_name, Persons.last_name == last_name)
            )
            parent_id = (await session.execute(parent_query)).scalar()

            if not parent_id:
                return []
            child_type = case((Persons.gender == "Мужской", "Сын"), else_="Дочь").label(
                "child_type"
            )
            query = (
                select(
                    Persons.first_name,
                    Persons.last_name,
                    Persons.father_name,
                    child_type,
                )
                .join(Relationship, Relationship.child_id == Persons.person_id)
                .where(Relationship.parent_id == parent_id)
            )
            result = await session.execute(query)
            return [dict(row._mapping) for row in result.all()]
    except Exception as e:
        print(f"Ошибка при получении детей: {e}")
        return []


async def get_user_by_id(user_id: int) -> Users | None:
    """Получает пользователя из базы данных по его идентификатору.

    Выполняет асинхронный запрос к базе данных для поиска записи в таблице 'users'
    с указанным user_id. Возвращает объект пользователя или None, если пользователь
    не найден. В случае ошибки выводит сообщение об ошибке и возвращает None.
    """
    try:
        async with async_session() as session:
            query = select(Users).where(Users.user_id == user_id)
            result = await asyncio.wait_for(session.execute(query), timeout=DB_TIMEOUT)
            return result.scalar_one_or_none()
    except TimeoutError:
        print(f"Таймаут при получении пользователя с user_id={user_id}")
        return None
    except Exception as e:
        print(f"Ошибка получения пользователя: {e}")
        return None


async def add_user(user_id: int, username: str) -> None:
    """Добавляет нового пользователя или обновляет существующего в базе данных.

    Использует upsert (INSERT ... ON CONFLICT DO UPDATE) для безопасного
    добавления пользователя. Если пользователь уже существует, обновляется username.
    """
    try:
        async with async_session() as session:
            stmt = pg_insert(Users).values(user_id=user_id, username=username)
            stmt = stmt.on_conflict_do_update(
                index_elements=["user_id"],
                set_={"username": username},
            )
            await asyncio.wait_for(session.execute(stmt), timeout=DB_TIMEOUT)
            await asyncio.wait_for(session.commit(), timeout=DB_TIMEOUT)
    except TimeoutError:
        print(f"Таймаут при добавлении пользователя с user_id={user_id}")
    except Exception as e:
        print(f"Ошибка добавления пользователя: {e}")
