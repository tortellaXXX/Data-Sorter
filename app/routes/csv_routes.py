from fastapi import APIRouter, Request, UploadFile, Form, Depends
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
import uuid
from sqlalchemy.orm import Session
from io import StringIO

# Импорт сервисов (теперь Postgres вместо Dremio)
from app.services import csv_service
from app.db.session import get_db

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
    db: Session = Depends(get_db),
):
    session_id = request.cookies.get("session_id") or str(uuid.uuid4())

    # читаем CSV
    contents = await file.read()
    df = csv_service.read_csv(contents)

    # проверяем колонку
    try:
        csv_service.check_column(df, sort_column)
    except ValueError as e:
        return csv_service.create_html_error(str(e))

    # делаем предпросмотр
    preview_html = csv_service.generate_preview_html(df, sort_column)

    # сохраняем в БД
    csv_service.save_csv_to_db(contents, db, session_id)

    # ответ
    response = templates.TemplateResponse(
        "result.html", {"request": request, "table_html": preview_html}
    )
    response.set_cookie("session_id", session_id)
    return response


# ---------- Скачивание CSV ----------
@router.get("/download")
async def download_csv(request: Request, db: Session = Depends(get_db)):
    session_id = request.cookies.get("session_id")
    if not session_id:
        return HTMLResponse("<h3>CSV еще не загружен</h3>")

    result_csv = csv_service.download_csv_from_db(db, session_id)
    if not result_csv:
        return HTMLResponse("<h3>Ошибка при получении данных</h3>")

    output = StringIO(result_csv)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=sorted.csv"},
    )
