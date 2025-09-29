#!/bin/bash
set -e

echo "Waiting for Dremio and creating admin user if needed..."

python3 - <<'EOF'
from app.utils.helpers import wait_for_dremio

# Ждём готовности Dremio и получаем токен
token = wait_for_dremio()
EOF

echo "Starting FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
