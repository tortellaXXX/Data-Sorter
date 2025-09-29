import requests
import time
import os
import uuid
import tempfile

# Берём из окружения
DREMIO_HOST = os.environ.get("DREMIO_HOST", "http://dremio:9047")
DREMIO_USER = os.environ.get("DREMIO_USER", "admin")
DREMIO_PASSWORD = os.environ.get("DREMIO_PASSWORD", "password")
DREMIO_SPACE = os.environ.get("DREMIO_SPACE", "MySpace")


def generate_session_id() -> str:
    """Генерация уникального идентификатора сессии"""
    return str(uuid.uuid4())


def create_temp_csv(contents: str) -> str:
    """Создание временного CSV файла и возврат его пути"""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    temp_file.write(contents.encode("utf-8"))
    temp_file.close()
    return temp_file.name


def wait_for_dremio_ready(timeout=300, interval=5):
    """
    Ждём готовности Dremio API.
    Для первого запуска API может отвечать 403 — это нормально.
    """
    print("Waiting for Dremio API to be ready...")
    start = time.time()
    login_url = f"{DREMIO_HOST}/apiv2/login"

    while time.time() - start < timeout:
        try:
            r = requests.post(login_url, json={"userName": DREMIO_USER, "password": DREMIO_PASSWORD})
            if r.status_code == 200:
                print("Dremio API is ready!")
                return
            elif r.status_code == 403:
                # Админ ещё не создан, это нормальный первый запуск
                print("Dremio API alive, admin user probably missing (first start).")
                return
            else:
                print(f"Got status {r.status_code}, retrying...")
        except requests.exceptions.RequestException:
            print("Dremio not ready yet...")
        time.sleep(interval)

    raise TimeoutError("Dremio API did not become ready in time")


def create_first_admin_user():
    """
    Создаём первого пользователя без токена (первый запуск Dremio)
    """
    users_url = f"{DREMIO_HOST}/api/v3/user"
    payload = {
        "userName": DREMIO_USER,
        "password": DREMIO_PASSWORD,
        "firstName": "Admin",
        "lastName": "User",
        "email": "admin@example.com",
        "roles": ["admin"]
    }
    try:
        r = requests.post(users_url, json=payload)
        if r.status_code in (200, 201):
            print("Admin user created!")
        elif r.status_code in (403, 409):
            print("Admin user already exists or forbidden (normal for first setup).")
        else:
            r.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to create admin user: {e}")


def get_dremio_token(retries=10, interval=5) -> str:
    """
    Логинимся и получаем токен после создания пользователя.
    Делает несколько попыток, пока Dremio не станет полностью готов.
    """
    url = f"{DREMIO_HOST}/apiv2/login"
    payload = {"userName": DREMIO_USER, "password": DREMIO_PASSWORD}

    for attempt in range(retries):
        try:
            r = requests.post(url, json=payload)
            if r.status_code == 200:
                token = r.json()["token"]
                print("Token obtained successfully!")
                return token
            elif r.status_code == 403:
                print(f"Attempt {attempt+1}/{retries}: Admin user not ready yet, retrying...")
        except requests.exceptions.RequestException:
            print(f"Attempt {attempt+1}/{retries}: Dremio not responding, retrying...")
        time.sleep(interval)

    raise TimeoutError("Failed to obtain Dremio token after retries")


def wait_and_create_admin() -> str:
    """
    Полный процесс: ждём готовности Dremio, создаём админа при первом запуске,
    возвращаем токен для использования в приложении.
    """
    wait_for_dremio_ready()
    create_first_admin_user()
    token = get_dremio_token()
    return token
