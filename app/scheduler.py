import datetime
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from sqlalchemy import func, select, cast, Integer, extract

from app.models import async_session, Persons, Users


async def birthday_notification():
    """
    Выбирает из БД персон, у которых сегодня день рождения,
    сравнивая день и месяц даты рождения (год не учитываем).
    """
    moscow_tz = pytz.timezone('Europe/Moscow')
    today = datetime.datetime.now(moscow_tz).date()

    async with async_session() as session:
        stmt = select(Persons).where(
            cast(extract('day', Persons.birth_date), Integer) == today.day,
            cast(extract('month', Persons.birth_date), Integer) == today.month
        )
        result = await session.execute(stmt)
        persons = result.scalars().all()
    return persons


async def get_all_users():
    """
    Получает всех пользователей из таблицы Users.
    Предполагается, что в таблице хранится user_id телеграм-пользователя.
    """
    async with async_session() as session:
        stmt = select(Users)
        result = await session.execute(stmt)
        users = result.scalars().all()
    return users


async def send_birthday_notifications(bot: Bot):
    """
    Запрашивает из БД персон с днём рождения, формирует сообщение
    и отправляет его каждому пользователю, зарегистрированному в таблице Users.
    Если записей с днем рождения нет, сообщение не отправляется.
    """
    persons = await birthday_notification()
    if persons:
        message_lines = ["Сегодня день рождения:"]
        for person in persons:
            message_lines.append(f"- {person.first_name} {person.last_name}")
        message = "\n".join(message_lines)
        users = await get_all_users()
        for user in users:
            try:
                await bot.send_message(chat_id=user.user_id, text=message)
                print(f"Сообщение отправлено пользователю {user.user_id}")
            except Exception as e:
                print(f"Ошибка при отправке сообщения пользователю {user.user_id}: {e}")
    else:
        print("Не найдено людей с днем рождения на сегодня")


def start_scheduler(bot: Bot):
    """
    Инициализация и запуск APScheduler с настройкой на московское время.
    Задача срабатывает каждый день в 9:00 по Москве и отправляет уведомления всем пользователям.
    """
    scheduler = AsyncIOScheduler(timezone='Europe/Moscow')

    scheduler.add_job(
        send_birthday_notifications,
        trigger="cron",
        hour=9,
        minute=0,
        args=[bot]
    )

    scheduler.start()