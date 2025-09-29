import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Подключаем маршруты
from app.routes.csv_routes import router as csv_router

# Подключаем базу и создаем таблицы
from app.db.session import engine, Base

# ---------- Инициализация базы ----------
Base.metadata.create_all(bind=engine)

# ---------- Создаем FastAPI приложение ----------
app = FastAPI(title="CSV Sorter with Dremio & Multiuser")

# ---------- Подключаем статические файлы ----------
app.mount("/static", StaticFiles(directory="static"), name="static")

# ---------- Подключаем шаблоны ----------
templates = Jinja2Templates(directory="templates")

# ---------- Подключаем маршруты ----------
app.include_router(csv_router)

# -----------------------------
# Если запускаем напрямую (python -m app.main)
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)