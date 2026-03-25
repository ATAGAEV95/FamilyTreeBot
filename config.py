# TG_TOKEN = 'Ваш токен телеграмм бота'

# Ваше подключение к БД Postgres
# DATABASE_URL = "postgresql+asyncpg://login:password@host:port/bdname"

# Ваша схема из БД Postgres, по умолчанию "public"
# SCHEMA = "public"


# Удалить код ниже если вы не используете CI/CD
import os

from dotenv import load_dotenv

load_dotenv()

TG_TOKEN = os.getenv("TG_TOKEN")

DATABASE_URL = os.getenv("DATABASE_URL")

SCHEMA = "public"
