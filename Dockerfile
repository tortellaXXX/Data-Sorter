# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем проект в контейнер
COPY . .

# Переменные окружения
ENV PYTHONUNBUFFERED=1

# Запускаем FastAPI через uvicorn через скрипт entrypoint
CMD ["python", "-m", "app.main"]
