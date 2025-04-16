from flask import Flask, jsonify
import cv2
import time
import json
import google.generativeai as genai
from PIL import Image
import pymysql
import numpy as np

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

def extract_product_info_from_image(frame):
    pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    try:
        response = model.generate_content([ 
            "Extract the product details from this image in JSON format. Only return JSON with keys: name, brand, product_type, size, expiry, price, sku.",
            pil_image
        ])
        raw_text = response.text.strip()
        print(f"🧾 Gemini raw:\n{raw_text}")

        if raw_text.startswith("```json"):
            raw_text = raw_text.replace("```json", "").replace("```", "").strip()

        data = json.loads(raw_text)
        return data
    except Exception as e:
        print("❌ Error processing Gemini response:", e)
        return None

app = Flask(__name__)

@app.route('/start_realtime_scan', methods=['GET'])
def start_realtime_scan():
    try:
        cap = cv2.VideoCapture(1)  # Use 0 or 1 depending on your webcam index
        scan_interval = 5  # seconds between scans
        last_scan_time = 0

        print("📷 Real-time scan started. Press 'q' in the window to stop.")

        while True:
            ret, frame = cap.read()
            if not ret:
                return jsonify({"error": "Camera not available"}), 500

            current_time = time.time()
            cv2.imshow("Real-Time Scanner Feed", frame)

            if current_time - last_scan_time > scan_interval:
                product_data = extract_product_info_from_image(frame)
                if product_data:
                    insert_into_database(product_data)
                    print("🟢 Product processed:", product_data)
                else:
                    print("⚠️ Could not extract product info.")
                last_scan_time = current_time

            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("🛑 Scanning stopped by user.")
                break

        cap.release()
        cv2.destroyAllWindows()
        return jsonify({"message": "Real-time scan completed"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port = 5000)
