from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from bs4 import BeautifulSoup
from fastapi.staticfiles import StaticFiles
from requests_html import AsyncHTMLSession
from fastapi import HTTPException
import time
import subprocess
import uuid
import shutil
import os
import asyncio
from pathlib import Path
from pyppeteer import launch
import pyppdf.patch_pyppeteer
import sys
import cv2
import numpy as np
from ultralytics import YOLO
from concurrent.futures import ThreadPoolExecutor
from fastapi import File, UploadFile
import io
import base64
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse


model = YOLO("train9/weights/best.pt")



if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


app = FastAPI()

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")



@app.post("/detect/")
async def detect_objects(file: UploadFile):
    try:
        # Convert the uploaded file to a NumPy array
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Perform object detection
        results = model.predict(image)
        
        # If the results have a 'render' method, use it to draw the detection results on the image
        if hasattr(results, 'render'):
            for img in results.render():
                image = img
        
        # Convert the processed image back to a format suitable for web (JPEG or PNG)
        _, buffer = cv2.imencode('.jpg', image)
        
        # Encode the image buffer to base64
        encoded_image = base64.b64encode(buffer).decode("utf-8")
        
        # Return the base64 encoded image
        return JSONResponse(content={"image": encoded_image})
    except Exception as e:
        print(f"Error: {str(e)}")  # Add more detailed logging
        raise HTTPException(status_code=500, detail=str(e))


def run_capture_script():
    # Assuming the capture script is located at a specific path
    result = subprocess.run(['node', 'capture.js'], capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout
    else:
        raise Exception(f"Script error: {result.stderr}")


@app.get("/show-results", response_class=FileResponse)
async def show_results():
    return "prediction.html"  # Replace with the path to your HTML file

@app.get("/screenshot")
async def screenshot():
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        try:
            screenshot_url = "/static/screenshots/screenshot.png"

            result = await loop.run_in_executor(pool, run_capture_script)
            # Success, return or process result
            return {"message": "Screenshot taken successfully", "url": screenshot_url}
        except Exception as e:
            return {"error": str(e)}



@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/beginner", response_class=HTMLResponse)
async def read_beginner(request: Request):
    return templates.TemplateResponse("beginner.html", {"request": request})
