#!/bin/sh
set -e

# Проверяем, что все нужные переменные окружения установлены
: "${DREMIO_HOST:?Need to set DREMIO_HOST}"
: "${DREMIO_USER:?Need to set DREMIO_USER}"
: "${DREMIO_PASSWORD:?Need to set DREMIO_PASSWORD}"
: "${DREMIO_PAT:?Need to set DREMIO_PAT}"

echo "Waiting for Dremio and creating admin user if needed..."

# Ждём Dremio и создаём админа через новый API с PAT
python - <<END
import os
from app.utils.helpers import wait_and_create_admin

# Передаём переменные окружения в модуль
os.environ['DREMIO_HOST'] = os.environ['DREMIO_HOST']
os.environ['DREMIO_USER'] = os.environ['DREMIO_USER']
os.environ['DREMIO_PASSWORD'] = os.environ['DREMIO_PASSWORD']
os.environ['DREMIO_PAT'] = os.environ['DREMIO_PAT']

wait_and_create_admin()
END

echo "Starting FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
