from flask import Flask, jsonify, Response
import cv2
import json
import google.generativeai as genai
from PIL import Image
import pymysql
import time

app = Flask(__name__)

# 🔐 Gemini Config
genai.configure(api_key="AIzaSyB9gKOT0r4k73X5i-Gt6JNpfLMxWq3HUa8")
model = genai.GenerativeModel("gemini-2.0-flash")

# 📦 MySQL DB Config
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "ritik@01A",
    "database": "product_database"
}

# Function to insert data into MySQL database
def insert_into_database(data):
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        query = """
            INSERT INTO product_info (name, brand, product_type, size, expiry, price, sku)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            data.get("name", ""),
            data.get("brand", ""),
            data.get("product_type", ""),
            data.get("size", ""),
            data.get("expiry", ""),
            data.get("price", ""),
            data.get("sku", "")
        )
        cursor.execute(query, values)
        conn.commit()
        conn.close()
        print("✅ Inserted product info into DB.")
    except Exception as e:
        print("❌ DB insert failed:", e)

# Function to extract product info using Gemini
def extract_product_info_from_image(frame):
    pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    try:
        response = model.generate_content([
            "Extract the product details from this image in JSON format. Only return JSON with keys: name, brand, product_type, size, expiry, price, sku.",
            pil_image
        ])
        raw_text = response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text.replace("```json", "").replace("```", "").strip()

        data = json.loads(raw_text)
        return data
    except Exception as e:
        print("❌ Error processing Gemini response:", e)
        return None

# Capture frames from the camera and process them
def generate_frames():
    cap = cv2.VideoCapture(1)  # Use external camera, or 0 for built-in webcam
    last_capture_time = 0
    scan_interval = 3  # seconds

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        current_time = time.time()

        # Scan the frame every scan_interval seconds
        if current_time - last_capture_time >= scan_interval:
            print("🔍 Capturing frame and processing...")
            product_data = extract_product_info_from_image(frame)
            if product_data:
                insert_into_database(product_data)
            last_capture_time = current_time

        # Encode the frame to JPEG and send it to the client
        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            break
        frame_bytes = jpeg.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')

    cap.release()

# Video streaming route. This will return the video feed to the client in real-time.
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Root endpoint to check if API is running
@app.route("/", methods=["GET"])
def index():
    return "🧠 Real-Time Product Scanner Flask API is running!"

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
