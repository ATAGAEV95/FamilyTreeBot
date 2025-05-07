import asyncio

from aiogram import Bot, Dispatcher

from app.handlers import router
from app.models import init_models
from app.scheduler import start_scheduler
from config import TG_TOKEN


async def main():
    bot = Bot(token=TG_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    start_scheduler(bot)
    await init_models()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())