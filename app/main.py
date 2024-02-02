from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.staticfiles import StaticFiles


app = FastAPI()

# Set up Jinja2 Templates
templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/beginner", response_class=HTMLResponse)
async def read_beginner(request: Request):
    return templates.TemplateResponse("beginner.html", {"request": request})
