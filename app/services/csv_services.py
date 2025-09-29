# app/services/csv_service.py

import pandas as pd
from io import StringIO
from fastapi.responses import HTMLResponse
from app.utils.helpers import create_temp_csv, generate_session_id

def read_csv(contents: bytes) -> pd.DataFrame:
    """
    Чтение CSV из байтов и возврат DataFrame
    """
    return pd.read_csv(StringIO(contents.decode("utf-8")))

def check_column(df: pd.DataFrame, column: str):
    """
    Проверка, есть ли колонка в DataFrame
    """
    if column not in df.columns:
        raise ValueError(f"Колонки '{column}' нет в файле. Доступные: {list(df.columns)}")

def generate_preview_html(df: pd.DataFrame, sort_column: str, rows: int = 20) -> str:
    """
    Возврат HTML таблицы первых n строк после сортировки
    """
    df_sorted = df.sort_values(by=sort_column)
    return df_sorted.head(rows).to_html(classes="table", index=False)

def create_html_error(message: str):
    """
    Возврат HTML ошибки
    """
    return HTMLResponse(f"<h3>{message}</h3>")

def save_temp_csv(contents: bytes) -> str:
    """
    Создаёт временный CSV и возвращает путь к файлу
    """
    csv_str = contents.decode("utf-8")
    return create_temp_csv(csv_str)

def create_session_id() -> str:
    """
    Генерация уникального ID сессии
    """
    return generate_session_id()
