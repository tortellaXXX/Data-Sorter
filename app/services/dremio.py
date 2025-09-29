import os
import time
import requests
import pandas as pd

# --- Конфигурация ---
DREMIO_HOST = os.environ.get("DREMIO_HOST", "http://dremio:9047")
DREMIO_USER = os.environ.get("DREMIO_USER", "admin")
DREMIO_PASSWORD = os.environ.get("DREMIO_PASSWORD", "password")
DREMIO_SPACE = os.environ.get("DREMIO_SPACE", "MySpace")


def _wait_for_token(timeout: int = 300, interval: int = 10) -> str:
    """
    Ожидаем готовности Dremio и получаем токен.
    Возвращает токен либо поднимает TimeoutError.
    """
    login_url = f"{DREMIO_HOST}/apiv2/login"
    start = time.time()
    print("⌛ Waiting for Dremio to accept login...")

    while time.time() - start < timeout:
        try:
            resp = requests.post(login_url, json={"userName": DREMIO_USER, "password": DREMIO_PASSWORD})
            if resp.status_code == 200:
                token = resp.json().get("token")
                print("✅ Got Dremio token")
                return token
            else:
                print(f"Login failed ({resp.status_code}), retrying...")
        except requests.exceptions.RequestException as e:
            print(f"Dremio not responding: {e}, waiting...")

        time.sleep(interval)

    raise TimeoutError("❌ Dremio did not become ready in time")


def _ensure_space_exists(token: str) -> None:
    """
    Проверяем, существует ли пространство. Если нет — создаём.
    """
    headers = {"Authorization": f"_dremio{token}"}
    resp = requests.get(f"{DREMIO_HOST}/api/v3/catalog", headers=headers)

    if resp.status_code == 200:
        for space in resp.json().get("data", []):
            if space.get("name") == DREMIO_SPACE:
                print(f"ℹ️ Space '{DREMIO_SPACE}' already exists")
                return

    payload = {"entityType": "space", "name": DREMIO_SPACE}
    resp = requests.post(f"{DREMIO_HOST}/api/v3/catalog", headers=headers, json=payload)

    if resp.status_code in (200, 201):
        print(f"✅ Space '{DREMIO_SPACE}' created successfully")
    elif resp.status_code == 409:
        print(f"ℹ️ Space '{DREMIO_SPACE}' already exists")
    else:
        raise RuntimeError(f"❌ Failed to create space: {resp.status_code} {resp.text}")


def get_dremio_token() -> str:
    """
    Получаем рабочий токен (ждём готовности сервера).
    """
    return _wait_for_token()


def upload_csv_to_dremio(csv_bytes: bytes, table_name: str) -> bool:
    """
    Загружает CSV в Dremio в указанное пространство.
    Возвращает True при успехе.
    """
    token = get_dremio_token()
    _ensure_space_exists(token)

    url = f"{DREMIO_HOST}/api/v3/catalog/{DREMIO_SPACE}/{table_name}/files"
    headers = {"Authorization": f"_dremio{token}"}
    files = {"file": ("file.csv", csv_bytes, "text/csv")}

    try:
        resp = requests.post(url, headers=headers, files=files)
        if resp.status_code in (200, 201):
            print(f"✅ CSV uploaded to table '{table_name}' successfully")
            return True
        else:
            print(f"❌ Failed to upload CSV: {resp.status_code} - {resp.text}")
            return False
    except Exception as e:
        print(f"❌ Error uploading CSV: {e}")
        return False


def query_dremio(sql_query: str) -> str:
    """
    Выполняет SQL-запрос и возвращает результат в формате CSV (строкой).
    """
    token = get_dremio_token()
    url = f"{DREMIO_HOST}/api/v3/sql"
    headers = {"Authorization": f"_dremio{token}", "Content-Type": "application/json"}
    payload = {"sql": sql_query}

    try:
        resp = requests.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        df = pd.DataFrame(data["rows"], columns=[col["name"] for col in data["columns"]])
        return df.to_csv(index=False)
    except Exception as e:
        print(f"❌ Error querying Dremio: {e}")
        return ""
