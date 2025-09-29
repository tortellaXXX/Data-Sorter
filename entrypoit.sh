#!/bin/sh
set -e

# Ждём Dremio и создаём админа
python -c "from app.utils.helpers import wait_and_create_admin; wait_and_create_admin()"

# Запускаем FastAPI через uvicorn
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
