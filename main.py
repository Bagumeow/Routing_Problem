from fastapi import FastAPI, File, Form, UploadFile, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import pandas as pd

from tools.vrp import VRP_Sol 
from tools.tools import take_tuple_latlong,plot_latlong_routing

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

global_df = None

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
async def upload_file(request: Request, csvfile: UploadFile = File(...)):
    global global_df
    df = pd.read_csv(csvfile.file)
    df = df[df['Seq'] != 'Last']
    global_df = df
    unique_provinces = df['mart_province'].unique().tolist()
    return templates.TemplateResponse("index.html", {"request": request, "provinces": unique_provinces})

@app.post("/filter-by-province")
async def filter_by_province(request: Request, province: str = Form(...)):
    global global_df
    if global_df is not None:
        global_df = global_df[global_df['mart_province'] == province]
        unique_dates = global_df['order_creation'].unique().tolist()
        return templates.TemplateResponse("index.html", {"request": request, "provinces": [province], "dates": unique_dates, "selected_province": province})
    else:
        return {"error": "No data available. Please upload a CSV file."}

@app.post("/filter-by-date")
async def filter_by_date(request: Request, order_creation: str = Form(...)):
    global global_df
    if global_df is not None:
        filtered_df = global_df[global_df['order_creation'] == order_creation]
        filtered_df['tuple_Latlong'] = filtered_df['Latlong'].apply(take_tuple_latlong)
        list_latlong = filtered_df['tuple_Latlong'].unique()
        sol_province = VRP_Sol(list_latlong, 3, 0)
        list_routing_vrp, _ = sol_province.solving_vrp(3)
        map_representation = plot_latlong_routing(list_latlong, list_routing_vrp)
        map_html = map_representation._repr_html_()
        return  HTMLResponse(content=map_html)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)