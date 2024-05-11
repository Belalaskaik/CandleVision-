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
from fastapi.middleware.cors import CORSMiddleware
import requests
import json 




model = YOLO("train9/weights/best.pt")
API_KEY ="MSOGTFCDJCZDCMRU"
API_URL = "https://www.alphavantage.co/query"


if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


app = FastAPI()



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Specify domains for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


class StockDataResponse(BaseModel):
    symbol: str
    last_price: float
    previous_close_price: float
    trend: str

def fetch_stock_price_change(symbol: str):
    """
    Fetches the most recent closing price and the closing price from 24 hours ago.
    """
    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": symbol,
        "interval": "60min",
        "apikey": API_KEY,
        "outputsize": "compact"  # Use 'full' for more historical data
    }
    response = requests.get(API_URL, params=params)
    data = response.json()
    if "Time Series (60min)" not in data:
        return None

    # Process the data
    time_series = data["Time Series (60min)"]
    sorted_times = sorted(time_series.keys())
    last_close = float(time_series[sorted_times[-1]]["4. close"])
    prev_close = float(time_series[sorted_times[-25]]["4. close"]) if len(sorted_times) > 24 else last_close

    # Determine trend
    trend = "bullish" if last_close > prev_close else "bearish" if last_close < prev_close else "neutral"

    return StockDataResponse(
        symbol=symbol,
        last_price=last_close,
        previous_close_price=prev_close,
        trend=trend
    )

@app.get("/api/stock/{symbol}", response_model=StockDataResponse)
async def get_stock_data(symbol: str):
    stock_data = fetch_stock_price_change(symbol)
    if stock_data:
        return stock_data
    else:
        raise HTTPException(status_code=404, detail="Stock data not found")

def get_element_screenshot(url: str, css_selector: str) -> bytes:
    API_KEY = 'af7837dbba2f473d9c8aa5b62ec673c0'
    # Construct the API URL with the element selector
    API_URL = f"https://api.apiflash.com/v1/urltoimage?access_key={API_KEY}&url={url}&element={css_selector}"

    response = requests.get(API_URL)
    if response.status_code == 200:
        return response.content
    else:
        raise Exception("Failed to capture screenshot")


@app.get("/element_screenshot/")
async def element_screenshot(url: str, selector: str):
    try:
        image_bytes = get_element_screenshot(url, selector)
        # You could save or directly serve this image as needed
        return {"message": "Screenshot of element taken successfully", "url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class DetectionResult(BaseModel):
    image: str
    patterns: List[str] 

class SmsRequest(BaseModel):
    detected_pattern_name: str

class CandlestickPattern(BaseModel):
    name: str
    description: str
    image_url: str



@app.get("/stock-tug-of-war", response_class=HTMLResponse)
async def stock_tug_of_war(request: Request):
    return templates.TemplateResponse("stock_tug_of_war.html", {"request": request})

@app.get("/api/stock/{symbol}")
async def get_stock_data(symbol: str):
    try:
        # Your existing function to fetch stock data
        stock_data = fetch_stock_price_change(symbol)
        if stock_data:
            return stock_data
        else:
            raise HTTPException(status_code=404, detail="Stock data not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/send-sms/")
async def send_sms(request_data: SmsRequest):
    account_sid = 'AC112ad13e45d59d15ab6f16504e06aad9'
    auth_token = 'eb1800d54673714bb4773446ed5905ec'
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
    x1 = 100       # Start from the middle of the width
    y1 = 98               # Start from the top edge of the image
    x2 = width - 70      # End at the right edge of the image
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


patterns: List[CandlestickPattern] = []
@app.post("/detect/")
async def detect_objects():
    try:
        detection_dir = "static/detections/"
        os.makedirs(detection_dir, exist_ok=True)

        # Assuming the image to detect is always the cropped screenshot
        input_image_path = "static/cropped/screenshot.png"
        output_image_path = f"{detection_dir}result.png"

        # Perform inference on the test image
        results = model.predict(input_image_path, conf=0.1)

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



@app.on_event("startup")
async def load_patterns():
    global patterns
    try:
        with open("patterns.json", "r") as file:
            patterns_data = json.load(file)
            patterns = [CandlestickPattern(**pattern) for pattern in patterns_data]
            print("Loaded patterns:", [pattern.dict() for pattern in patterns])  # Optional: to verify that patterns are loaded correctly
    except Exception as e:
        print(f"Failed to load patterns: {str(e)}")


@app.get("/patterns/{pattern_name}", response_model=CandlestickPattern)
async def get_pattern(pattern_name: str):
    for pattern in patterns:
        if pattern.name.lower() == pattern_name.lower():
            return pattern
    raise HTTPException(status_code=404, detail="Pattern not found")


# def run_capture_script():
#     # Assuming the capture script is located at a specific path
#     result = subprocess.run(['node', 'capture.js'], capture_output=True, text=True)

#     if result.returncode == 0:
        
#         return result.stdout
#     else:
#         raise Exception(f"Script error: {result.stderr}")

def capture_screenshot(url, output_path):
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Ensure GUI is off
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Set path to chromedriver as needed
    driver = webdriver.Chrome(executable_path='/path/to/chromedriver', options=chrome_options)

    try:
        driver.get(url)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.tradingview-widget-container1')))
        
        # Screenshot of entire page
        driver.save_screenshot(output_path)
    finally:
        driver.quit()

@app.get("/show-results", response_class=FileResponse)
async def show_results():
    return "prediction.html"  # Replace with the path to your HTML file



# @app.get("/screenshot")
# async def screenshot():
#     loop = asyncio.get_event_loop()
#     with ThreadPoolExecutor() as pool:
#         try:
#             screenshot_url = "/static/screenshots/screenshot.png"

#             result = await loop.run_in_executor(pool, run_capture_script)
#             # Success, return or process result
#             return {"message": "Screenshot taken successfully", "url": screenshot_url}
#         except Exception as e:
#             return {"error": str(e)}
def capture_element_screenshot(url, css_selector, api_key, output_path):
    """
    Captures a screenshot of a specific element on a webpage using the ApiFlash API.
    """
    params = {
        'access_key': api_key,
        'url': url,
        'element': css_selector,
        'format': 'png'
    }
    
    response = requests.get("https://api.apiflash.com/v1/urltoimage", params=params)
    
    if response.status_code == 200:
        with open(output_path, 'wb') as file:
            file.write(response.content)
        return output_path
    else:
        raise Exception(f"Failed to capture screenshot: {response.status_code} - {response.text}")

@app.get("/screenshot/")
async def screenshot():
    API_KEY = 'af7837dbba2f473d9c8aa5b62ec673c0'  # Use your ApiFlash API key
    URL = 'https://fastapi-app-04xj.onrender.com/'
    CSS_SELECTOR = '#tradingview-widget'  # The specific element to capture
    OUTPUT_FILE = 'static/screenshots/screenshot.png'  # Path to save the screenshot
    
    try:
        output_path = capture_element_screenshot(URL, CSS_SELECTOR, API_KEY, OUTPUT_FILE)
        return {"message": "Screenshot taken successfully", "url": OUTPUT_FILE}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("beginner.html", {"request": request})

@app.get("/beginner", response_class=HTMLResponse)
async def read_beginner(request: Request):
    return templates.TemplateResponse("beginner.html", {"request": request})
