import requests
import time
from requests.auth import HTTPBasicAuth
from app.services.dremio import DREMIO_HOST, DREMIO_USER, DREMIO_PASSWORD
import uuid
import tempfile

def generate_session_id() -> str:
    return str(uuid.uuid4())

def create_temp_csv(contents: str) -> str:
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    temp_file.write(contents.encode("utf-8"))
    temp_file.close()
    return temp_file.name

def wait_for_dremio(timeout=180, interval=5):
    """Ждём, пока Dremio API не станет доступен с Basic Auth"""
    print("Waiting for Dremio API to be ready...")
    start = time.time()
    users_url = f"{DREMIO_HOST}/api/v3/user"

    while time.time() - start < timeout:
        try:
            r = requests.get(users_url, auth=HTTPBasicAuth(DREMIO_USER, DREMIO_PASSWORD))
            if r.status_code == 200:
                print("Dremio API is ready!")
                return True
            else:
                print(f"API returned {r.status_code}, retrying...")
        except requests.exceptions.RequestException as e:
            print(f"API not ready yet: {e}")
        time.sleep(interval)

    raise TimeoutError("Dremio API did not become ready in time")

def create_admin_user_if_not_exists(retries=3, interval=5):
    """Создаём администратора, если его нет (Basic Auth)"""
    users_url = f"{DREMIO_HOST}/api/v3/user"

    for attempt in range(retries):
        try:
            resp = requests.get(users_url, auth=HTTPBasicAuth(DREMIO_USER, DREMIO_PASSWORD))
            resp.raise_for_status()
            data = resp.json().get('data', [])
            users = [u['userName'] for u in data]
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
            r = requests.post(users_url, auth=HTTPBasicAuth(DREMIO_USER, DREMIO_PASSWORD), json=payload)
            r.raise_for_status()
            print("Admin user created.")
            return
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt+1}/{retries} failed: {e}")
            time.sleep(interval)

    raise RuntimeError("Failed to create admin user after retries")

def wait_and_create_admin():
    wait_for_dremio()
    create_admin_user_if_not_exists()
