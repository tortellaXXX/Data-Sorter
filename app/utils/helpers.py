import requests
import time
from app.services.dremio import DREMIO_HOST, DREMIO_USER, DREMIO_PASSWORD, DREMIO_PAT
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

def wait_for_dremio(timeout=180):
    """Ждём, пока Dremio не станет доступен для логина"""
    print("Waiting for Dremio to be ready...")
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(f"{DREMIO_HOST}/api/v3/login")  # проверяем новый API
            if r.status_code == 200:
                print("Dremio is ready!")
                return True
        except:
            pass
        time.sleep(5)
    raise TimeoutError("Dremio did not start in time")

def create_admin_user_if_not_exists():
    """Создаёт администратора, если его нет, через новый API /api/v3/user и PAT"""
    headers = {"Authorization": f"Bearer {DREMIO_PAT}"}

    # Проверяем, существует ли пользователь
    users_url = f"{DREMIO_HOST}/api/v3/user"
    resp = requests.get(users_url, headers=headers)
    resp.raise_for_status()
    users = [u['userName'] for u in resp.json()['data']]

    if DREMIO_USER in users:
        print("Admin user already exists.")
        return

    # Создаём пользователя, если нет
    payload = {
        "userName": DREMIO_USER,
        "password": DREMIO_PASSWORD,
        "firstName": "Admin",
        "lastName": "User",
        "email": "admin@example.com",
        "roles": ["admin"]
    }
    r = requests.post(users_url, headers=headers, json=payload)
    r.raise_for_status()
    print("Admin user created.")

def wait_and_create_admin():
    """Ждём Dremio и создаём администратора"""
    wait_for_dremio()
    create_admin_user_if_not_exists()