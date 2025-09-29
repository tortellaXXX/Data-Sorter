import uvicorn
import pandas as pd
from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from io import StringIO

app = FastAPI()

# Подключим статик
app.mount("/static", StaticFiles(directory="static"), name="static")

# Главная страница с drag-and-drop
@app.get("/", response_class=HTMLResponse)
async def root_html():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()

# Обработка CSV и сортировка
@app.post("/sort")
async def sort_df(file: UploadFile, sort_column: str = Form(...)):
    # 1. Прочитать CSV в pandas
    contents = await file.read()
    df = pd.read_csv(StringIO(contents.decode("utf-8")))

    # 2. Отсортировать по выбранной колонке
    if sort_column not in df.columns:
        return {"error": f"Колонки '{sort_column}' нет в файле. Доступные: {list(df.columns)}"}

    df_sorted = df.sort_values(by=sort_column)

    return {
        "status": "ok",
        "columns": list(df_sorted.columns),
        "preview": df_sorted.head(50).to_dict(orient="records")
    }

#    # 3. Сохранить результат в память и вернуть пользователю
#   output = StringIO()
#    df_sorted.to_csv(output, index=False)
#    output.seek(0)

#    return StreamingResponse(
#       output,
#        media_type="text/csv",
#        headers={"Content-Disposition": f"attachment; filename=sorted.csv"}
#    )


if __name__ == '__main__':
    uvicorn.run(app, 
                host='127.0.0.1', 
                port=8000)  

