# FamilyTreeBot

**FamilyTreeBot** — это Telegram-бот для поиска информации из вашей базы данных о родственниках и друзьях по имени и фамилии.  
Проект реализован на Python с использованием библиотеки **aiogram** и базы данных **PostgreSQL**.  
Данный бот предназначен только для просмотра информации.  
Но прежде всего необходимо запустить бот [PersonnelManagerBot](https://github.com/ATAGAEV95/PersonnelManagerBot) для администрирования этих данных.

---

## Описание проекта

FamilyTreeBot помогает быстро находить сведения о людях из вашей личной базы — достаточно написать имя и фамилию в чате с ботом, чтобы получить, например, дату рождения. Также бот отправляет ежедневные напоминания о днях рождения ваших близких.

---

## Технологии

| Компонент   | Используемое решение            |
|-------------|---------------------------------|
| Язык        | Python 3.10+                    |
| Библиотека  | aiogram                         |
| Планировщик | APScheduler                     |
| СУБД        | PostgreSQL                      |
| ORM         | SQLAlchemy                      |

---

## Возможности

- Просмотр информации о родственниках и друзьях
- Быстрый поиск по имени и фамилии
- Ежедневные уведомления о днях рождения
- Поддержка нескольких Telegram-пользователей

---

## Как это работает

1. Пользователь отправляет имя и фамилию прямо в чат с ботом.
2. Бот ищет совпадения в базе данных и выводит найденные данные.
3. Ежедневно всем пользователям отправляются напоминания о днях рождения.

---

## Предварительные настройки бота

Необходимо внести изменения в файл [config.py](https://github.com/ATAGAEV95/FamilyTreeBot/blob/develop/config.py), удалив всё, оставив только следующее:
```python
TG_TOKEN = 'Ваш токен телеграм-бота'

# Ваше подключение к БД Postgres
DATABASE_URL = "postgresql+asyncpg://login:password@host:port/bdname"

# Схема базы данных Postgres, по умолчанию "public"
SCHEMA = "public"
```
Замените `TG_TOKEN` на ваш токен телеграм-бота.  
В строке `DATABASE_URL` замените следующие параметры:  
- `login` — логин базы данных  
- `password` — пароль базы данных  
- `host` — хост базы данных (например, 192.168.0.1)  
- `port` — порт базы данных (обычно 5432 для Postgres)  
- `bdname` — название базы данных

---

## Пароль для бота

Пароль необходимо указать в файле [handlers.py](https://github.com/ATAGAEV95/FamilyTreeBot/blob/develop/app/handlers.py) в строке:
```python
ACCESS_PASSWORD = 'e5ae93bd8095fbd86c25a110bbf194a5a1a209f1e8eb31bb30c8b0ecbe254d58'
```
Это значение представляет собой хэш-пароль, сгенерированный с использованием хэш-функции.  
Чтобы получить подобное значение, используйте функцию `hash_password`:
```python
import hashlib

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

print(hash_password('12345678'))  # ef797c8118f02dfb649607dd5d3f8c7623048c9c063d532cc95c5ed7a898a64f
```
Вы можете использовать любой свой пароль — сгенерированный хэш необходимо присвоить переменной `ACCESS_PASSWORD`.

---

## Как запустить бота

Чтобы создать Docker-образ, перейдите в корневой каталог проекта в терминале и выполните команду:
```bash
docker build . -t familytreebot
```
Для запуска контейнера Docker выполните:
```bash
docker run -d --name fambot familytreebot
```
Для просмотра запущенных контейнеров:
```bash
docker ps
```
Чтобы остановить и, при необходимости, удалить контейнер:
```bash
docker stop fambot
docker rm fambot
```

---

## CI/CD

Если вы решили сделать Fork репозитория и настроить CI/CD для автоматического деплоя изменений бота, не вносите изменения в файл [config.py](https://github.com/ATAGAEV95/FamilyTreeBot/blob/develop/config.py).  
Файл [docker-image.yml](https://github.com/ATAGAEV95/FamilyTreeBot/blob/develop/.github/workflows/docker-image.yml) содержит конфигурацию CI/CD:

Деплой бота на удалённый сервер Ubuntu происходит по `ssh` при выполнении `push` или `pull request` в основную ветку `main`, а также при ручном запуске в разделе Actions:
```yaml
on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]
```
На удалённом сервере Ubuntu должен быть установлен Docker, а в домашней директории пользователя создана папка `~/deploy`:
```yaml
target: "~/deploy/"
```

Для настройки CI/CD выполните следующие шаги:  
Перейдите в раздел репозитория → `Settings` → `Secrets and variables` → `Actions` → `New repository secret` и добавьте последовательно следующие параметры:  
- `DATABASE_URL` — строка подключения в формате `"postgresql+asyncpg://login:password@host:port/bdname"`.
- `TG_TOKEN` — токен телеграм-бота (без кавычек).
- `DEPLOY_SERVER_HOST` — адрес хоста удалённого сервера Ubuntu.
- `DEPLOY_SERVER_PASSWORD` — пароль пользователя на удалённом сервере Ubuntu (например, `root`).
- `DEPLOY_SERVER_USER` — имя пользователя на удалённом сервере Ubuntu.

---