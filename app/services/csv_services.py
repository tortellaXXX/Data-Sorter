# app/services/csv_service.py

import pandas as pd
import io
import uuid
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.db.models import UserTable


def read_csv(contents: bytes, encoding: str = "utf-8") -> pd.DataFrame:
    """
    Чтение CSV из байтов в DataFrame
    """
    return pd.read_csv(io.BytesIO(contents), encoding=encoding)


def check_column(df: pd.DataFrame, column: str) -> None:
    """
    Проверка, есть ли колонка в DataFrame
    """
    if column not in df.columns:
        raise ValueError(f"Колонки '{column}' нет. Доступные: {list(df.columns)}")


def generate_preview_html(
    df: pd.DataFrame, sort_column: str, rows: int = 20, ascending: bool = True
) -> str:
    """
    Возвращает HTML таблицу первых n строк после сортировки
    """
    df_sorted = df.sort_values(by=str(sort_column), ascending=ascending)
    return df_sorted.head(rows).to_html(classes="table", index=False)


def create_html_error(message: str) -> HTMLResponse:
    """
    Возвращает HTML ошибки
    """
    return HTMLResponse(f"<h3>{message}</h3>")


def save_csv_to_db(contents: bytes, db: Session, session_id: str) -> str:
    """
    Загружает CSV в Postgres как отдельную таблицу и сохраняет в UserTable
    """
    df = pd.read_csv(io.BytesIO(contents))

    # Генерим имя таблицы
    table_name = f"table_{uuid.uuid4().hex[:8]}"

    # Загружаем в Postgres
    df.to_sql(table_name, con=db.get_bind(), if_exists="replace", index=False)

    # Обновляем/создаем запись о пользователе
    db_user_table = UserTable(session_id=session_id, table_name=table_name)
    db.merge(db_user_table)
    db.commit()

    return table_name


def download_csv_from_db(db: Session, session_id: str) -> str | None:
    """
    Загружает CSV из Postgres для текущего пользователя
    """
    user_table = db.query(UserTable).filter(UserTable.session_id == session_id).first()
    if not user_table:
        return None

    sql = f'SELECT * FROM "{user_table.table_name}"'
    df = pd.read_sql(sql, db.get_bind())

    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)

    return output.getvalue()
