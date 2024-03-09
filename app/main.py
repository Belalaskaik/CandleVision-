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
from concurrent.futures import ThreadPoolExecutor


if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


app = FastAPI()


app.mount("/static", StaticFiles(directory="static"), name="static")

def run_capture_script():
    # Assuming the capture script is located at a specific path
    result = subprocess.run(['node', 'capture.js'], capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout
    else:
        raise Exception(f"Script error: {result.stderr}")

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

# @app.get("/screenshot")
# async def take_screenshot(background_tasks: BackgroundTasks):
#     # Use a background task to not block the API while taking the screenshot
#     background_tasks.add_task(run_capture_script)
#     return FileResponse(SCREENSHOT_PATH)


# PROJECT_ROOT = Path(__file__).parent
# CAPTURE_SCRIPT_PATH = PROJECT_ROOT / 'capture.js'


# async def run_capture_script():
#     try:
#         # Run the capture.js script asynchronously
#         process = await asyncio.create_subprocess_exec(
#             'node', str(CAPTURE_SCRIPT_PATH),
#             stdout=asyncio.subprocess.PIPE,
#             stderr=asyncio.subprocess.PIPE,
#             cwd=str(PROJECT_ROOT))  # Set the working directory to your project root
#         stdout, stderr = await process.communicate()
#         if process.returncode != 0:
#             print(f"Capture script exited with error: {stderr.decode()}")
#         else:
#             print(f"Screenshot captured successfully. Output:\n{stdout.decode()}")
#     except Exception as e:
#         print(f"Error executing capture script: {e}")

# @app.get("/screenshot")
# async def take_screenshot():
#     # Await the completion of the screenshot capture
#     await run_capture_script()
#     # Once the capture is complete, return the new screenshot
#     return FileResponse(SCREENSHOT_PATH)
# # C:\Users\belal\Desktop\spring 2024\CandleVisionGit\CandleVision-\capture.js
# @app.get("/execute-script")
# async def execute_script():
#     # Construct an absolute path to the script.js file
#     script_path = "C:\\Users\\belal\\Desktop\\spring 2024\\CandleVisionGit\\CandleVision-\\capture.js"

#     try:
#         # Ensure 'node' command is available & the path to script.js is correct
#         result = subprocess.run(['node', script_path], capture_output=True, text=True, check=True)
#         return {"message": "Script executed successfully", "script_output": result.stdout}
#     except subprocess.CalledProcessError as e:
#         return {"error": "Script execution failed", "message": e.stderr}
#     except FileNotFoundError:
#         return {"error": "Node.js is not installed or script.js not found"}
templates = Jinja2Templates(directory="templates")




@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/beginner", response_class=HTMLResponse)
async def read_beginner(request: Request):
    return templates.TemplateResponse("beginner.html", {"request": request})




