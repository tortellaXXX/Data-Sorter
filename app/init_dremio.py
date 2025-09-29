import os
import sys
import time
import requests

# --- Конфигурация ---
DREMIO_HOST = os.environ.get("DREMIO_HOST", "http://dremio:9047")
DREMIO_USER = os.environ.get("DREMIO_USER", "admin")
DREMIO_PASSWORD = os.environ.get("DREMIO_PASSWORD", "password")
DREMIO_SPACE = os.environ.get("DREMIO_SPACE", "MySpace")


def wait_for_dremio(timeout: int = 300, interval: int = 10) -> bool:
    """
    Ждем, пока Dremio HTTP API станет доступен.
    Возвращает True, если готов; False, если вышло время.
    """
    start = time.time()
    print(f"⌛ Waiting for Dremio at {DREMIO_HOST} ...")
    while time.time() - start < timeout:
        try:
            resp = requests.get(DREMIO_HOST, timeout=5)
            if resp.status_code in (200, 401):
                print("✅ Dremio HTTP endpoint is up")
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(interval)
    return False


def bootstrap_first_user() -> None:
    """
    Создание первого пользователя (bootstrap).
    Если уже создан — пропускаем.
    """
    payload = {
        "userName": DREMIO_USER,
        "firstName": "Admin",
        "lastName": "User",
        "email": "admin@example.com",
        "createdAt": 0,
        "password": DREMIO_PASSWORD,
    }
    resp = requests.post(f"{DREMIO_HOST}/apiv2/bootstrap/firstuser", json=payload)

    if resp.status_code == 200:
        print("✅ Admin user created successfully")
    elif resp.status_code == 400:
        print("ℹ️ User already exists, skipping bootstrap")
    else:
        sys.exit(f"❌ Bootstrap failed: {resp.status_code} {resp.text}")


def login() -> str:
    """
    Авторизация и получение токена.
    Возвращает токен, либо завершает работу с кодом 1.
    """
    payload = {"userName": DREMIO_USER, "password": DREMIO_PASSWORD}
    resp = requests.post(f"{DREMIO_HOST}/apiv2/login", json=payload)

    if resp.status_code == 200:
        token = resp.json().get("token")
        print("✅ Logged in successfully")
        return token

    sys.exit(f"❌ Login failed: {resp.status_code} {resp.text}")


def create_space(token: str) -> None:
    """
    Создание Space, если его ещё нет.
    """
    headers = {"Authorization": f"_dremio{token}"}
    resp = requests.post(
        f"{DREMIO_HOST}/api/v3/catalog",
        headers=headers,
        json={"entityType": "space", "name": DREMIO_SPACE},
    )

    if resp.status_code in (200, 201):
        print(f"✅ Space '{DREMIO_SPACE}' created")
    elif resp.status_code == 409:
        print(f"ℹ️ Space '{DREMIO_SPACE}' already exists")
    else:
        sys.exit(f"❌ Failed to create space: {resp.status_code} {resp.text}")


if __name__ == "__main__":
    if not wait_for_dremio():
        sys.exit("❌ Dremio did not become ready in time")

    bootstrap_first_user()
    token = login()
    create_space(token)

    print("🎉 Dremio initialization complete!")
