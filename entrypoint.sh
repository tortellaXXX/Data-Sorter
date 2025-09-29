#!/bin/bash
set -e

echo "Waiting for Dremio and creating admin user if needed..."

# Выполняем Python-скрипт inline для создания админа и получения токена
TOKEN=$(python3 - <<'EOF'
import os
from app.utils.helpers import wait_and_create_admin

token = wait_and_create_admin()
print(token)  # Выводим токен, чтобы его можно было использовать или логировать
EOF
)

echo "Dremio admin ready. Token obtained: $TOKEN"

echo "Starting FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
