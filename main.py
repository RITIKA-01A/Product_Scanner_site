# from fastapi import FastAPI, File, UploadFile
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from PIL import Image
# import io
# import json
# import google.generativeai as genai
# import pymysql
# import re

# # --- Gemini + DB Configs ---
# genai.configure(api_key="AIzaSyB9gKOT0r4k73X5i-Gt6JNpfLMxWq3HUa8")
# model = genai.GenerativeModel("gemini-2.0-flash")

# DB_CONFIG = {
#     "host": "localhost",
#     "user": "root",
#     "password": "ritik@01A",
#     "database": "product_database"
# }

# # --- Insert into DB ---
# def insert_into_database(data):
#     try:
#         conn = pymysql.connect(**DB_CONFIG)
#         cursor = conn.cursor()
#         query = """
#             INSERT INTO product_info (name, brand, product_type, size, expiry, price, sku)
#             VALUES (%s, %s, %s, %s, %s, %s, %s)
#         """
#         values = (
#             data.get("name", ""),
#             data.get("brand", ""),
#             data.get("product_type", ""),
#             data.get("size", ""),
#             data.get("expiry", ""),
#             data.get("price", ""),
#             data.get("sku", "")
#         )
#         cursor.execute(query, values)
#         conn.commit()
#         conn.close()
#         print("✅ Inserted into DB.")
#     except Exception as e:
#         print("❌ DB Error:", e)

# # --- Extract from Image ---
# def extract_info_from_image(image_bytes):
#     try:
#         pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
#         response = model.generate_content(
#             [
#                 """You are an AI OCR system. From the image provided, extract product details and output ONLY a JSON object with the following keys: 
#                 name, brand, product_type, size, expiry, price, sku.
#                 Return only the JSON object. Do not include any explanation or markdown formatting like ```.""",
#                 pil_image
#             ],
#             generation_config={
#                 "temperature": 0.3,
#                 "top_p": 1,
#                 "top_k": 40,
#                 "max_output_tokens": 512,
#             },
#             safety_settings={
#                 "HARASSMENT": "block_none",
#                 "HATE": "block_none",
#                 "SEXUAL": "block_none",
#                 "DANGEROUS": "block_none",
#             }
#         )

#         raw_text = response.text.strip()
#         print("🔍 Gemini Response:", repr(raw_text))

#         match = re.search(r"\{[\s\S]*\}", raw_text)
#         if match:
#             json_data = match.group(0)
#             return json.loads(json_data)
#         else:
#             print("⚠ No valid JSON object found in Gemini response.")
#             return {"raw_response": raw_text, "error": "No valid JSON object found"}
#     except Exception as e:
#         print("❌ Gemini Error:", e)
#         return {"raw_response": "", "error": str(e)}

# # --- FastAPI App ---
# app = FastAPI()

# # --- CORS ---
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000"],  # Replace with your frontend IP
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # --- Image Upload Endpoint ---
# @app.post("/scan-image")
# async def scan_image(file: UploadFile = File(...)):
#     try:
#         image_bytes = await file.read()
#         extracted_data = extract_info_from_image(image_bytes)
#         if "error" not in extracted_data:
#             insert_into_database(extracted_data)
#             return {"message": "Image scanned and saved", "data": extracted_data}
#         else:
#             return {"message": "Failed to extract data", "data": extracted_data}
#     except Exception as e:
#         return {"error": str(e)}




# from flask import Flask, jsonify
# import cv2
# import json
# from PIL import Image
# import google.generativeai as genai

# # 🔐 Gemini Config
# genai.configure(api_key="AIzaSyB9gKOT0r4k73X5i-Gt6JNpfLMxWq3HUa8")
# model = genai.GenerativeModel("gemini-2.0-flash")

# app = Flask(__name__)

# def extract_product_info_from_image(frame):
#     pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
#     try:
#         response = model.generate_content([
#             "Extract the product details from this image in JSON format. Only return JSON with keys: name, brand, product_type, size, expiry, price, sku.",
#             pil_image
#         ])
#         raw_text = response.text.strip()
#         if raw_text.startswith("```json"):
#             raw_text = raw_text.replace("```json", "").replace("```", "").strip()

#         data = json.loads(raw_text)

#         if isinstance(data, list):
#             data = sorted(data, key=lambda x: sum(bool(v) for v in x.values()), reverse=True)[0]

#         return {"status": "success", "data": data}

#     except Exception as e:
#         return {"status": "error", "message": str(e)}

# @app.route("/capture", methods=["GET"])
# def capture_and_extract():
#     cap = cv2.VideoCapture(0)
#     if not cap.isOpened():
#         return jsonify({"status": "error", "message": "Failed to open camera"}), 500

#     ret, frame = cap.read()
#     cap.release()

#     if not ret:
#         return jsonify({"status": "error", "message": "Failed to capture image"}), 500

#     result = extract_product_info_from_image(frame)

#     if result["status"] == "success":
#         return jsonify(result)
#     else:
#         return jsonify(result), 500

# if __name__ == "__main__":
#     app.run(port="0.0.0.0",host = 5000,debug=True)






from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import cv2
import json
from PIL import Image
import google.generativeai as genai

# 🔐 Gemini Config
genai.configure(api_key="AIzaSyB9gKOT0r4k73X5i-Gt6JNpfLMxWq3HUa8")
model = genai.GenerativeModel("gemini-2.0-flash")

app = FastAPI()

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

        if isinstance(data, list):
            data = sorted(data, key=lambda x: sum(bool(v) for v in x.values()), reverse=True)[0]

        return {"status": "success", "data": data}

    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/capture")
def capture_and_extract():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise HTTPException(status_code=500, detail="Failed to open camera")

    ret, frame = cap.read()
    cap.release()

    if not ret:
        raise HTTPException(status_code=500, detail="Failed to capture image")

    result = extract_product_info_from_image(frame)

    if result["status"] == "success":
        return JSONResponse(content=result)
    else:
        raise HTTPException(status_code=500, detail=result["message"])
