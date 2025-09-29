# helpers.py
import uuid
import tempfile

# --- Вспомогательные функции ---
def generate_session_id() -> str:
    """Генерация уникального идентификатора сессии"""
    return str(uuid.uuid4())

def create_temp_csv(contents: str) -> str:
    """Создание временного CSV файла и возврат его пути"""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    temp_file.write(contents.encode("utf-8"))
    temp_file.close()
    return temp_file.name
