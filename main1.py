from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
import threading
import cv2
import time
import json
from PIL import Image
import pymysql
import google.generativeai as genai
from io import BytesIO

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to ["http://localhost:3000"] for production
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gemini + MySQL
genai.configure(api_key="YOUR_GEMINI_API_KEY")
model = genai.GenerativeModel("gemini-2.0-flash")
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "ritik@01A",
    "database": "product_database"
}

def insert_into_database(data):
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        query = """INSERT INTO product_info (name, brand, product_type, size, expiry, price, sku)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(query, (
            data.get("name", ""), data.get("brand", ""), data.get("product_type", ""),
            data.get("size", ""), data.get("expiry", ""), data.get("price", ""), data.get("sku", "")
        ))
        conn.commit()
        conn.close()
        print("✅ Inserted product info into DB.")
    except Exception as e:
        print("❌ DB insert failed:", e)

def extract_product_info_from_image(frame):
    pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    try:
        response = model.generate_content([
            "Extract the product details from this image in JSON format. Only return JSON with keys: name, brand, product_type, size, expiry, price, sku.",
            pil_image
        ])
        raw_text = response.text.strip()
        print(f"🧾 Gemini raw:\n{raw_text}")
        if raw_text.startswith("json"):
            raw_text = raw_text.replace("json", "").replace("```", "").strip()
        data = json.loads(raw_text)
        return data
    except Exception as e:
        print("❌ Error processing Gemini response:", e)
        return None

# ---------------- Camera Control ----------------

camera_on = False
cap = None
last_frame = None

def scanner_loop():
    global cap, camera_on, last_frame
    last_capture_time = 0
    interval = 3

    while camera_on and cap:
        success, frame = cap.read()
        if not success:
            break
        last_frame = frame.copy()

        if time.time() - last_capture_time >= interval:
            print("🔍 Scanning...")
            result = extract_product_info_from_image(frame)
            if result:
                insert_into_database(result)
            last_capture_time = time.time()

        time.sleep(0.01)  # Slight pause to reduce CPU load

@app.post("/start-scanner")
def start_scanner():
    global camera_on, cap
    if not camera_on:
        cap = cv2.VideoCapture(0)
        camera_on = True
        threading.Thread(target=scanner_loop).start()
        return {"status": "started"}
    return {"status": "already running"}

@app.post("/stop-scanner")
def stop_scanner():
    global camera_on, cap
    camera_on = False
    if cap:
        cap.release()
        return {"status": "stopped"}
    return {"status": "not active"}

@app.get("/video-feed")
def video_feed():
    def generate():
        while camera_on:
            if last_frame is not None:
                _, buffer = cv2.imencode('.jpg', last_frame)
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            time.sleep(0.1)
    return StreamingResponse(generate(), media_type="multipart/x-mixed-replace; boundary=frame")