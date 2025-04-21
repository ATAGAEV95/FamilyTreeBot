import asyncio
from aiogram import Bot, Dispatcher

from config import TG_TOKEN
from app.handlers import router
from app.scheduler import start_scheduler


async def main():
    bot = Bot(token=TG_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    start_scheduler(bot)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())