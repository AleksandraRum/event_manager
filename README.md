# Event Manager

REST API для управления мероприятиями на Django REST Framework.

## Стек

- Python 3.13
- Django 5.2
- Django REST Framework
- PostgreSQL
- Redis
- Celery + Celery Beat
- Pytest

## Функциональность

- Создание и получение списка мероприятий.
- Регистрация участников с учётом свободных мест.
- Списание и возврат бонусов.
- Отмена регистрации.
- Профиль пользователя с последними 10 регистрациями.
- Расчёт количества участников и среднего рейтинга.
- Фоновые напоминания через Celery.

## Запуск проекта

1. Создать виртуальное окружение и установить зависимости:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Создать `.env` на основе `.env.example` и заполнить переменные окружения.

3. Запустить PostgreSQL и Redis:

```bash
docker compose up -d
```

4. Выполнить миграции:

```bash
python manage.py migrate
```

5. Запустить Django:

```bash
python manage.py runserver
```

6. В отдельных терминалах запустить Celery Worker и Beat:

```bash
celery -A config worker --loglevel=info --pool=solo
```

```bash
celery -A config beat --loglevel=info
```

## API

| Метод | Endpoint | Описание |
|---|---|---|
| GET | `/api/events/` | Список мероприятий |
| POST | `/api/events/` | Создание мероприятия |
| POST | `/api/events/{id}/register/` | Регистрация |
| GET | `/api/profile/me/` | Профиль пользователя |

## Тестирование

```bash
python -m pytest -v
```

## Проверка качества кода

```bash
ruff check .
ruff format --check .
```