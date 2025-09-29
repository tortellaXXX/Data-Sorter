FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Запускаем скрипт инициализации и затем приложение
CMD ["sh", "-c", "python -c 'import time; time.sleep(30)' && uvicorn app.main:app --host 0.0.0.0 --port 8000"]