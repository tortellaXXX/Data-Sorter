from fastapi import APIRouter, Request, UploadFile, Form, Depends
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from io import StringIO
import pandas as pd
import uuid
from sqlalchemy.orm import Session

# Импорт сервисов
from app.services import dremio
from app.db.session import get_db
from app.db.models import UserTable

import os

DREMIO_SPACE = os.environ.get("DREMIO_SPACE", "MySpace")

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

    contents = await file.read()
    df = pd.read_csv(StringIO(contents.decode("utf-8")))

    if sort_column not in df.columns:
        return HTMLResponse(
            f"<h3>Колонки '{sort_column}' нет в файле. Доступные: {list(df.columns)}</h3>"
        )

    preview_html = df.sort_values(sort_column).head(20).to_html(classes="table", index=False)

    table_name = f"table_{uuid.uuid4().hex}"
    if dremio.upload_csv_to_dremio(contents, table_name):
        db_user_table = UserTable(session_id=session_id, dremio_table=table_name)
        db.add(db_user_table)
        db.commit()
    else:
        return HTMLResponse("<h3>Ошибка при загрузке CSV в Dremio</h3>")

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

    user_table = db.query(UserTable).filter(UserTable.session_id == session_id).first()
    if not user_table:
        return HTMLResponse("<h3>CSV еще не загружен</h3>")

    result_csv = dremio.query_dremio(f'SELECT * FROM "{DREMIO_SPACE}"."{user_table.dremio_table}"')
    if not result_csv:
        return HTMLResponse("<h3>Ошибка при запросе к Dremio</h3>")

    output = StringIO(result_csv)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=sorted.csv"},
    )
