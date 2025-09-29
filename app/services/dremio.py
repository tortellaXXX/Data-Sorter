# dremio.py
import os
import time
import requests
import pandas as pd
import uuid
import tempfile

# ------------------------------
# Конфигурация Dremio через окружение
# ------------------------------
DREMIO_HOST = os.environ.get("DREMIO_HOST", "http://dremio:9047")
DREMIO_USER = os.environ.get("DREMIO_USER", "admin")
DREMIO_PASSWORD = os.environ.get("DREMIO_PASSWORD", "password")
DREMIO_SPACE = os.environ.get("DREMIO_SPACE", "MySpace")


# ------------------------------
# Пользователи и токены
# ------------------------------
def wait_for_dremio_ready(timeout=300, interval=5):
    """Ждём готовности Dremio API (для первого запуска может быть 403)"""
    print("Waiting for Dremio API to be ready...")
    start = time.time()
    login_url = f"{DREMIO_HOST}/apiv2/login"

    while time.time() - start < timeout:
        try:
            r = requests.post(login_url, json={"userName": DREMIO_USER, "password": DREMIO_PASSWORD})
            if r.status_code in (200, 403):
                print("Dremio API is ready!")
                return
        except requests.exceptions.RequestException:
            pass
        print("Dremio not ready yet, retrying...")
        time.sleep(interval)

    raise TimeoutError("Dremio API did not become ready in time")


def create_first_admin_user():
    """Создаём первого администратора при первом запуске"""
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
            print("Admin user already exists (normal for first setup).")
        else:
            r.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to create admin user: {e}")


def get_dremio_token(retries=10, interval=5) -> str:
    """Получение токена авторизации Dremio с повторными попытками"""
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
                print(f"Attempt {attempt+1}/{retries}: Admin user not ready, retrying...")
        except requests.exceptions.RequestException:
            print(f"Attempt {attempt+1}/{retries}: Dremio not responding, retrying...")
        time.sleep(interval)

    raise TimeoutError("Failed to obtain Dremio token after retries")


def wait_and_create_admin() -> str:
    """
    Полный процесс первого запуска:
    - Ждём готовности API
    - Создаём администратора
    - Возвращаем токен для работы
    """
    wait_for_dremio_ready()
    create_first_admin_user()
    return get_dremio_token()


# ------------------------------
# Работа с CSV и SQL
# ------------------------------
def upload_csv_to_dremio(csv_bytes: bytes, table_name: str) -> bool:
    """Загрузка CSV в Dremio как таблицу"""
    token = wait_and_create_admin()
    url = f"{DREMIO_HOST}/api/v3/catalog/{DREMIO_SPACE}/{table_name}/files"
    headers = {"Authorization": f"_dremio{token}"}
    files = {"file": ("file.csv", csv_bytes)}
    r = requests.post(url, headers=headers, files=files)
    r.raise_for_status()
    print(f"CSV uploaded to table '{table_name}' successfully")
    return True


def query_dremio(sql_query: str) -> str:
    """Выполнение SQL-запроса и возврат результата в CSV"""
    token = wait_and_create_admin()
    url = f"{DREMIO_HOST}/api/v3/sql"
    headers = {
        "Authorization": f"_dremio{token}",
        "Content-Type": "application/json"
    }
    payload = {"sql": sql_query}
    r = requests.post(url, headers=headers, json=payload)
    r.raise_for_status()
    data = r.json()
    df = pd.DataFrame(data["rows"], columns=data["columns"])
    return df.to_csv(index=False)

