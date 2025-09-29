from fastapi import APIRouter, Request, UploadFile, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from io import StringIO
import pandas as pd
import uuid


# Импорт сервисов (еще надо создать)
from app.services import csv_services
from app.services import dremio
from app.db.session import get_db
from app.db.models import UserTable

router = APIRouter()
templates = Jinja2Templates(directory="templates")


# ---------- Главная страница ----------
@router.get("/", response_class=HTMLResponse)
async def root_html(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# ---------- Загрузка CSV и сортировка ----------
@router.post("/sort", response_class=HTMLResponse)
async def sort_df(
    request: Request,
    file: UploadFile,
    sort_column: str = Form(...),
):
    """
    Загружает CSV, сохраняет таблицу в Dremio, сортирует по колонке
    и возвращает HTML предпросмотра первых 20 строк.
    """
    # Получаем или создаем session_id из cookie
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())

    # Считываем CSV и проверяем колонку
    contents = await file.read()
    df = pd.read_csv(StringIO(contents.decode("utf-8")))

    if sort_column not in df.columns:
        return HTMLResponse(
            f"<h3>Колонки '{sort_column}' нет в файле. Доступные: {list(df.columns)}</h3>"
        )

    # Сортировка через pandas для предпросмотра
    preview_html = df.sort_values(sort_column).head(20).to_html(classes="table", index=False)

    # Загружаем CSV в Dremio (сервис)
    table_name = f"table_{uuid.uuid4().hex}"
    dremio.upload_csv_to_dremio(contents, table_name)

    # Сохраняем соответствие session_id -> таблица Dremio в БД
    db = get_db()
    db_user_table = UserTable(session_id=session_id, dremio_table=table_name)
    db.add(db_user_table)
    db.commit()
    db.close()

    # Возвращаем HTML предпросмотра с cookie
    response = templates.TemplateResponse(
        "result.html", {"request": request, "table_html": preview_html}
    )
    response.set_cookie("session_id", session_id)
    return response


# ---------- Скачивание CSV ----------
@router.get("/download")
async def download_csv(request: Request):
    """
    Скачивание полной таблицы CSV из Dremio для текущей сессии
    """
    session_id = request.cookies.get("session_id")
    if not session_id:
        return HTMLResponse("<h3>CSV еще не загружен</h3>")

    # Получаем таблицу Dremio по session_id
    db = get_db()
    user_table = db.query(UserTable).filter(UserTable.session_id == session_id).first()
    db.close()
    if not user_table:
        return HTMLResponse("<h3>CSV еще не загружен</h3>")

    # SQL запрос к Dremio
    result_csv = dremio.query_dremio(f"SELECT * FROM MySpace.{user_table.dremio_table}")

    # Отправляем как CSV
    output = StringIO(result_csv)
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=sorted.csv"},
    )
