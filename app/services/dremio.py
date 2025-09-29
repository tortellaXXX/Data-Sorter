import os
import time
import requests
import pandas as pd

# Конфигурация
DREMIO_HOST = os.environ.get("DREMIO_HOST", "http://dremio:9047")
DREMIO_USER = os.environ.get("DREMIO_USER", "admin")
DREMIO_PASSWORD = os.environ.get("DREMIO_PASSWORD", "password")
DREMIO_SPACE = os.environ.get("DREMIO_SPACE", "MySpace")

def wait_for_dremio_ready(timeout=300, interval=10):
    """Wait for Dremio to be ready AND accept the admin credentials."""
    print("Waiting for Dremio API to be ready and accept credentials...")
    start = time.time()
    login_url = f"{DREMIO_HOST}/apiv2/login"

    while time.time() - start < timeout:
        try:
            r = requests.post(login_url, json={"userName": DREMIO_USER, "password": DREMIO_PASSWORD})
            if r.status_code == 200:  # Successfully logged in
                print("Dremio is ready and credentials are valid!")
                return
            else:
                # Log the failure, then wait to try again
                print(f"Login failed with status {r.status_code}. Retrying...")
        except requests.exceptions.RequestException as e:
            print(f"Dremio not responding: {e}, waiting...")
        time.sleep(interval)

    raise TimeoutError("Dremio did not become ready in time")

def ensure_space_exists(token):
    """Проверяем существование пространства и создаем если нужно"""
    headers = {"Authorization": f"_dremio{token}"}
    
    # Получаем список пространств
    r = requests.get(f"{DREMIO_HOST}/api/v3/catalog", headers=headers)
    if r.status_code == 200:
        spaces = r.json().get("data", [])
        for space in spaces:
            if space.get("name") == DREMIO_SPACE:
                print(f"Space '{DREMIO_SPACE}' already exists")
                return
    
    # Создаем пространство если не существует
    payload = {
        "entityType": "space",
        "name": DREMIO_SPACE
    }
    r = requests.post(f"{DREMIO_HOST}/api/v3/catalog", headers=headers, json=payload)
    if r.status_code in (200, 201):
        print(f"Space '{DREMIO_SPACE}' created successfully")
    else:
        print(f"Failed to create space: {r.status_code} - {r.text}")

def get_dremio_token():
    """Получаем токен Dremio"""
    return wait_for_dremio_ready()

def upload_csv_to_dremio(csv_bytes: bytes, table_name: str) -> bool:
    """Загрузка CSV в Dremio"""
    token = get_dremio_token()
    
    # Сначала убедимся что пространство существует
    ensure_space_exists(token)
    
    url = f"{DREMIO_HOST}/api/v3/catalog/{DREMIO_SPACE}/{table_name}/files"
    headers = {"Authorization": f"_dremio{token}"}
    files = {"file": ("file.csv", csv_bytes, "text/csv")}
    
    try:
        r = requests.post(url, headers=headers, files=files)
        if r.status_code in (200, 201):
            print(f"CSV uploaded to table '{table_name}' successfully")
            return True
        else:
            print(f"Failed to upload CSV: {r.status_code} - {r.text}")
            return False
    except Exception as e:
        print(f"Error uploading CSV: {e}")
        return False

def query_dremio(sql_query: str) -> str:
    """Выполнение SQL-запроса"""
    token = get_dremio_token()
    url = f"{DREMIO_HOST}/api/v3/sql"
    headers = {
        "Authorization": f"_dremio{token}",
        "Content-Type": "application/json"
    }
    payload = {"sql": sql_query}
    
    try:
        r = requests.post(url, headers=headers, json=payload)
        r.raise_for_status()
        data = r.json()
        df = pd.DataFrame(data["rows"], columns=[col["name"] for col in data["columns"]])
        return df.to_csv(index=False)
    except Exception as e:
        print(f"Error querying Dremio: {e}")
        return ""