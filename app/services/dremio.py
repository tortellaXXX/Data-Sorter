import requests
import pandas as pd
from io import StringIO

# Конфигурация Dremio
DREMIO_HOST = "http://localhost:9047"  # URL Dremio
DREMIO_USER = "your_user"
DREMIO_PASSWORD = "your_password"
DREMIO_SPACE = "MySpace"  # рабочее пространство Dremio

# Получение токена авторизации
def get_dremio_token():
    url = f"{DREMIO_HOST}/apiv2/login"
    payload = {"userName": DREMIO_USER, "password": DREMIO_PASSWORD}
    r = requests.post(url, json=payload)
    r.raise_for_status()
    return r.json()["token"]

# Загрузка CSV в Dremio как таблицу
def upload_csv_to_dremio(csv_bytes, table_name):
    """
    csv_bytes: bytes (содержимое файла)
    table_name: str (имя таблицы в Dremio)
    """
    token = get_dremio_token()
    url = f"{DREMIO_HOST}/api/v3/catalog/{DREMIO_SPACE}/{table_name}/files"
    headers = {"Authorization": f"_dremio{token}"}
    files = {"file": ("file.csv", csv_bytes)}
    r = requests.post(url, headers=headers, files=files)
    r.raise_for_status()
    return True

# Выполнение SQL-запроса и возврат CSV
def query_dremio(sql_query: str) -> str:
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

    # Конвертация в CSV через pandas
    df = pd.DataFrame(data["rows"], columns=data["columns"])
    return df.to_csv(index=False)
