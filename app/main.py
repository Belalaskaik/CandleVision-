from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from requests_html import AsyncHTMLSession
from fastapi import HTTPException
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
import time
import glob
from ultralytics.utils.plotting import Annotator, colors
from twilio.rest import Client
from pydantic import BaseModel
from typing import List





model = YOLO("train9/weights/best.pt")



if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


app = FastAPI()

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")



class DetectionResult(BaseModel):
    image: str
    patterns: List[str] 

class SmsRequest(BaseModel):
    detected_pattern_name: str


@app.post("/send-sms/")
async def send_sms(request_data: SmsRequest):
    account_sid = 'AC112ad13e45d59d15ab6f16504e06aad9'
    auth_token = '0d9445278c693d18be5008cd4e77b35c'

    client = Client(account_sid, auth_token)
    
    try:
        sms_body = f"Pattern Detected: {request_data.detected_pattern_name}"

        message = client.messages.create(
            from_='+18889912962',  # Twilio number
            body=sms_body,  # The message body
            to='+18777804236'  # Number to send the SMS to
        )
        return {"message": "SMS sent successfully", "sid": message.sid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def crop_image(image_path, save_path):
    """
    Crops the right side of the image at the specified image_path and saves it to save_path.
    
    Parameters:
    image_path (str): The file path of the image to crop.
    save_path (str): The file path where the cropped image will be saved.
    """
    # Load the screenshot image
    screenshot = cv2.imread(image_path)

    # Check if the image was loaded successfully
    if screenshot is None:
        print(f"Error: Could not load image from {image_path}")
        return

    # Get the dimensions of the screenshot
    height, width, _ = screenshot.shape

    # Define the region of interest (ROI) coordinates
    # Adjusted to crop the right side of the image
    x1 = width // 2       # Start from the middle of the width
    y1 = 98               # Start from the top edge of the image
    x2 = width - 90       # End at the right edge of the image
    y2 = height - 80      # End at the bottom edge of the image

    # Crop the image to the defined ROI
    cropped_image = screenshot[y1:y2, x1:x2]

    # Save the cropped image as a PNG file
    cv2.imwrite(save_path, cropped_image)
    print(f"Cropped image saved to {save_path}")


@app.post("/crop-screenshot/{filename}")
async def crop_screenshot(filename: str):
    input_path = f"static/screenshots/{filename}"
    cropped_path = f"static/cropped/{filename}"

    # Ensure the cropped directory exists
    os.makedirs("static/cropped", exist_ok=True)

    # Crop the image
    crop_image(input_path, cropped_path)

    # Build the URL for the cropped image
    url_to_cropped_image = f"/static/cropped/{filename}"

    # Return a JSON response containing the URL to the cropped image
    return JSONResponse(content={"url": url_to_cropped_image})



@app.post("/detect/")
async def detect_objects():
    try:
        detection_dir = "static/detections/"
        os.makedirs(detection_dir, exist_ok=True)

        # Assuming the image to detect is always the cropped screenshot
        input_image_path = "static/cropped/screenshot.png"
        output_image_path = f"{detection_dir}result.png"

        # Perform inference on the test image
        results = model.predict(input_image_path, conf=0.5)

        # Load the image for annotation
        img = cv2.imread(input_image_path)
        if img is None:
            raise Exception("Failed to load image for annotation.")

        # Check if there are detections and the 'boxes' attribute exists
        if results[0].boxes is not None:
            boxes = results[0].boxes.xyxy.cpu().tolist()  # Extract bounding box coordinates
            clss = results[0].boxes.cls.cpu().tolist()  # Extract class IDs

            annotator = Annotator(img, line_width=2, example=model.names)

            for box, cls in zip(boxes, clss):
                annotator.box_label(box, color=colors(int(cls), True), label=model.names[int(cls)])

            # Save the annotated image
            cv2.imwrite(output_image_path, annotator.result())

        else:
            raise Exception("No objects were detected in the image.")

        # Load the annotated image to send it back as a response
        with open(output_image_path, "rb") as image_file:
            image_data = image_file.read()

        patterns = [model.names[int(cls)] for cls in clss]  # Convert class IDs to pattern names

        # Encode the image buffer to base64 to send as JSON
        encoded_image = base64.b64encode(image_data).decode("utf-8")

        return DetectionResult(image=encoded_image, patterns=patterns)
    except Exception as e:
        print(f"Error: {str(e)}")
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
