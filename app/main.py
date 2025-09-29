import uvicorn
import pandas as pd
from fastapi import FastAPI, UploadFile, Form, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from io import StringIO

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def root_html(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/sort", response_class=HTMLResponse)
async def sort_df(request: Request, file: UploadFile, sort_column: str = Form(...)):
    contents = await file.read()
    df = pd.read_csv(StringIO(contents.decode("utf-8")))
    if sort_column not in df.columns:
        return HTMLResponse(f"<h3>Колонки '{sort_column}' нет в файле. Доступные: {list(df.columns)}</h3>")
    df_sorted = df.sort_values(by=sort_column)
    app.state.last_csv = df_sorted.to_csv(index=False)
    preview_html = df_sorted.head(20).to_html(classes="table", index=False)
    return templates.TemplateResponse("result.html", {"request": request, "table_html": preview_html})

@app.get("/download")
async def download_csv():
    if not hasattr(app.state, "last_csv"):
        return HTMLResponse("<h3>CSV еще не загружен</h3>")
    output = StringIO(app.state.last_csv)
    output.seek(0)
    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=sorted.csv"})

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
