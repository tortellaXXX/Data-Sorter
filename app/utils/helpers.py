# app/utils/helpers.py
import requests
import time
from app.services.dremio import DREMIO_HOST, DREMIO_USER, DREMIO_PASSWORD
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

def wait_for_dremio(timeout=120):
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(f"{DREMIO_HOST}/apiv2/login")
            if r.status_code == 200:
                return True
        except:
            pass
        time.sleep(5)
    raise TimeoutError("Dremio did not start in time")

def create_admin_user_if_not_exists():
    try:
        # Попытка залогиниться
        url = f"{DREMIO_HOST}/apiv2/login"
        payload = {"userName": DREMIO_USER, "password": DREMIO_PASSWORD}
        r = requests.post(url, json=payload)
        r.raise_for_status()
    except requests.exceptions.HTTPError:
        # Админ не существует — создаём
        url = f"{DREMIO_HOST}/apiv2/user"
        payload = {
            "userName": DREMIO_USER,
            "password": DREMIO_PASSWORD,
            "firstName": "Admin",
            "lastName": "User",
            "email": "admin@example.com",
            "roles": ["admin"]
        }
        r = requests.post(url, json=payload)
        r.raise_for_status()
        print("Admin user created")