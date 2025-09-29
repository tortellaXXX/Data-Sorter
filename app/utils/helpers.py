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
    return str(uuid.uuid4())

def create_temp_csv(contents: str) -> str:
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    temp_file.write(contents.encode("utf-8"))
    temp_file.close()
    return temp_file.name

def wait_for_dremio(timeout=300, interval=5) -> str:
    """Ждём готовности Dremio через /apiv2/login и возвращаем токен"""
    print("Waiting for Dremio API to be ready...")
    start = time.time()
    login_url = f"{DREMIO_HOST}/apiv2/login"

    while time.time() - start < timeout:
        try:
            r = requests.post(login_url, json={"userName": DREMIO_USER, "password": DREMIO_PASSWORD})
            if r.status_code == 200:
                token = r.json().get("token")
                print("Dremio API is ready!")
                return token
            else:
                print(f"API returned {r.status_code}, retrying...")
        except requests.exceptions.RequestException as e:
            print(f"API not ready yet: {e}")
        time.sleep(interval)

    raise TimeoutError("Dremio API did not become ready in time")

def create_admin_user_if_not_exists(token: str, retries=3, interval=5):
    """Создаём администратора через токен"""
    users_url = f"{DREMIO_HOST}/api/v3/user"
    headers = {"Authorization": f"_dremio{token}"}

    for attempt in range(retries):
        try:
            resp = requests.get(users_url, headers=headers)
            if resp.status_code == 404:
                # Если эндпоинт не найден, возможно, админ уже есть
                print("Admin user endpoint not found, skipping creation.")
                return
            resp.raise_for_status()
            data = resp.json().get("data", [])
            users = [u["userName"] for u in data]
            if DREMIO_USER in users:
                print("Admin user already exists.")
                return

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
            return
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt+1}/{retries} failed: {e}")
            time.sleep(interval)

    print("Failed to create admin user after retries")

def wait_and_create_admin():
    token = wait_for_dremio()
    create_admin_user_if_not_exists(token)
