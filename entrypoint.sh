#!/bin/bash
set -e

# Проверка, что переменные окружения установлены
: "${DREMIO_HOST:?Need to set DREMIO_HOST}"
: "${DREMIO_USER:?Need to set DREMIO_USER}"
: "${DREMIO_PASSWORD:?Need to set DREMIO_PASSWORD}"

echo "Waiting for Dremio and creating admin user if needed..."

# Ждём Dremio и создаём админа через логин/пароль
python3 - <<'EOF'
import os
from app.utils.helpers import wait_and_create_admin

# Передаём переменные окружения в модуль
os.environ['DREMIO_HOST'] = os.environ['DREMIO_HOST']
os.environ['DREMIO_USER'] = os.environ['DREMIO_USER']
os.environ['DREMIO_PASSWORD'] = os.environ['DREMIO_PASSWORD']

wait_and_create_admin()
EOF

echo "Starting FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload