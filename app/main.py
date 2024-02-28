from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from fastapi.staticfiles import StaticFiles
from requests_html import AsyncHTMLSession
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import subprocess
import uuid
import shutil
import os

app = FastAPI()


SCREENSHOT_DIR = "static/screenshots"
SCREENSHOT_PATH = os.path.join(SCREENSHOT_DIR, "screenshot.png")

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/screenshot")
async def take_screenshot(background_tasks: BackgroundTasks):
    # Use a background task to not block the API while taking the screenshot
    background_tasks.add_task(run_capture_script)
    return FileResponse(SCREENSHOT_PATH)

def run_capture_script():
    try:
        # Ensure the full path to `capture.js` is correct
        subprocess.run(["node", "capture.js"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing capture script: {e}")




templates = Jinja2Templates(directory="templates")



@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/beginner", response_class=HTMLResponse)
async def read_beginner(request: Request):
    return templates.TemplateResponse("beginner.html", {"request": request})




