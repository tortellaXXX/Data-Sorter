import os
import requests
import pandas as pd

# Конфигурация Dremio через переменные окружения
DREMIO_HOST = os.environ.get("DREMIO_HOST", "http://dremio:9047")
DREMIO_USER = os.environ.get("DREMIO_USER", "admin")
DREMIO_PASSWORD = os.environ.get("DREMIO_PASSWORD", "password")
DREMIO_SPACE = os.environ.get("DREMIO_SPACE", "MySpace")

def get_dremio_token() -> str:
    """Получение токена авторизации Dremio"""
    url = f"{DREMIO_HOST}/apiv2/login"
    payload = {"userName": DREMIO_USER, "password": DREMIO_PASSWORD}
    r = requests.post(url, json=payload)
    r.raise_for_status()
    return r.json()["token"]

def upload_csv_to_dremio(csv_bytes: bytes, table_name: str) -> bool:
    """Загрузка CSV в Dremio как таблицу"""
    token = get_dremio_token()
    url = f"{DREMIO_HOST}/api/v3/catalog/{DREMIO_SPACE}/{table_name}/files"
    headers = {"Authorization": f"_dremio{token}"}
    files = {"file": ("file.csv", csv_bytes)}
    r = requests.post(url, headers=headers, files=files)
    r.raise_for_status()
    return True

def query_dremio(sql_query: str) -> str:
    """Выполнение SQL-запроса и возврат CSV"""
    token = get_dremio_token()
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
