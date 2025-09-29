# app/utils/helpers.py

import uuid
import tempfile

def generate_session_id() -> str:
    """Генерирует уникальный ID для сессии пользователя"""
    return str(uuid.uuid4())

def create_temp_csv(contents: str) -> str:
    """Создаёт временный CSV-файл и возвращает путь к нему"""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    temp_file.write(contents.encode("utf-8"))
    temp_file.close()
    return temp_file.name
