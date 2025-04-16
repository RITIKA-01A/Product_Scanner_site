# from fastapi import FastAPI, HTTPException, File, UploadFile
# from fastapi.responses import JSONResponse
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from datetime import datetime
# import google.generativeai as genai
# import pymysql
# import cv2
# from PIL import Image
# import io
# import json
# import re

# # Gemini configuration
# genai.configure(api_key="AIzaSyB9gKOT0r4k73X5i-Gt6JNpfLMxWq3HUa8")
# model = genai.GenerativeModel("gemini-2.0-flash")

# # Database Configuration
# DB_CONFIG = {
#     "host": "localhost",
#     "user": "root",
#     "password": "ritik@01A",  # Ensure this is correct
#     "database": "scanner"
# }
# TABLE_NAME = "products"

# # FastAPI app init
# app = FastAPI()

# # CORS setup
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Update with frontend URL
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Pydantic model
# class Product(BaseModel):
#     name: str
#     brand: str
#     product_type: str
#     size: str
#     expiry: str
#     price: str
#     sku: str

# # Database table creation
# def setup_mysql():
#     conn = pymysql.connect(
#         host=DB_CONFIG["host"],
#         user=DB_CONFIG["user"],
#         password=DB_CONFIG["password"]
#     )
#     with conn.cursor() as cursor:
#         cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
#     conn.commit()
#     conn.close()

#     conn = pymysql.connect(**DB_CONFIG)
#     with conn.cursor() as cursor:
#         cursor.execute(f"""
#             CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
#                 id INT AUTO_INCREMENT PRIMARY KEY,
#                 name VARCHAR(255),
#                 brand VARCHAR(255),
#                 product_type VARCHAR(100),
#                 size VARCHAR(50),
#                 expiry VARCHAR(255), 
#                 price VARCHAR(50),
#                 sku VARCHAR(50)
#             )
#         """)
#     conn.commit()
#     conn.close()

# # Database connection function
# def get_db_connection():
#     conn = pymysql.connect(**DB_CONFIG)
#     return conn

# # Gemini OCR logic
# def extract_info_from_image(pil_image):
#     try:
#         response = model.generate_content(
#             [
#                 "Extract product details and return ONLY a JSON object with keys: name, brand, product_type, size, expiry, price, sku.",
#                 pil_image
#             ],
#             generation_config={"temperature": 0.3, "top_p": 1, "top_k": 40, "max_output_tokens": 512},
#             safety_settings={"HARASSMENT": "block_none", "HATE": "block_none", "SEXUAL": "block_none", "DANGEROUS": "block_none"},
#         )

#         raw_text = response.text.strip()
#         match = re.search(r"\{[\s\S]*\}", raw_text)
#         if match:
#             return {"status": "success", "data": json.loads(match.group(0))}
#         return {"status": "error", "message": "No valid JSON found"}
#     except Exception as e:
#         return {"status": "error", "message": str(e)}

# # DB insert logic
# def insert_into_database(data):
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor()

#         query = """
#         INSERT INTO products (name, price, sku, expiry, brand, product_type, size)
#         VALUES (%s, %s, %s, %s, %s, %s, %s)
#         """
#         values = (
#             data["name"],
#             data["price"],
#             data["sku"],
#             data["expiry"],
#             data["brand"],
#             data["product_type"],
#             data["size"]
#         )

#         cursor.execute(query, values)
#         conn.commit()
#         cursor.close()
#         conn.close()
#         return True
#     except Exception as e:
#         print("DB Insert Error:", e)
#         return False

# # File Upload Endpoint
# @app.post("/scan-image")
# async def scan_image(file: UploadFile = File(...)):
#     try:
#         print("called")
#         image_bytes = await file.read()
#         pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
#         result = extract_info_from_image(pil_image)

#         if result["status"] == "success":
#             success = insert_into_database(result["data"])
#             if success:
#                 return {"message": "Product extracted and saved", "data": result["data"]}
#             else:
#                 return {"message": "Data extraction successful, DB insert failed", "data": result["data"]}
#         else:
#             return {"message": "Extraction failed", "error": result["message"]}
#     except Exception as e:
#         return {"error": str(e)}

# # Camera Capture Endpoint
# @app.get("/capture")
# def capture_image_and_extract():
#     cap = cv2.VideoCapture(0)
#     if not cap.isOpened():
#         raise HTTPException(status_code=500, detail="Failed to open camera")

#     ret, frame = cap.read()
#     cap.release()

#     if not ret:
#         raise HTTPException(status_code=500, detail="Failed to capture image")

#     pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
#     result = extract_info_from_image(pil_image)

#     if result["status"] == "success":
#         success = insert_into_database(result["data"])
#         if success:
#             return {"message": "Captured, extracted, and saved", "data": result["data"]}
#         else:
#             return {"message": "Captured & extracted, but DB insert failed", "data": result["data"]}
#     else:
#         raise HTTPException(status_code=500, detail=result["message"])

# # Manual Add Product Endpoint
# @app.post("/add_product")
# async def add_product(product: Product):
#     try:
#         print("calledd")
#         data = product.dict()
#         print(data)
#         print(data["price"])
#         success = insert_into_database(data)
#         if success:
#             return {"message": "✅ Product manually added"}
#         else:
#             raise HTTPException(status_code=500, detail="❌ DB insert failed")
#     except ValueError:
#         raise HTTPException(status_code=400, detail="❌ Invalid expiry date format. Use DD/MM/YY")

# # On app startup
# @app.on_event("startup")
# def startup_event():
#     setup_mysql()

# # Host and port setup
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=5000)








from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import google.generativeai as genai
import pymysql
import cv2
from PIL import Image
import io
import json
import re

# Gemini configuration
genai.configure(api_key="AIzaSyB9gKOT0r4k73X5i-Gt6JNpfLMxWq3HUa8")
model = genai.GenerativeModel("gemini-2.0-flash")

# Database Configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "ritik@01A",
    "database": "scanner"
}
TABLE_NAME = "products"

# FastAPI app init
app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class Product(BaseModel):
    name: str
    brand: str
    product_type: str
    size: str
    expiry: str
    price: str
    sku: str
    email: str  # Foreign key field

class User(BaseModel):
    email: str
    username: str
    password: str

# Database table creation
def setup_mysql():
    conn = pymysql.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"]
    )
    with conn.cursor() as cursor:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
    conn.commit()
    conn.close()

    conn = pymysql.connect(**DB_CONFIG)
    with conn.cursor() as cursor:
        # Create users table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS users (
                email VARCHAR(255) PRIMARY KEY,
                username VARCHAR(100) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Create products table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255),
                brand VARCHAR(255),
                product_type VARCHAR(100),
                size VARCHAR(50),
                expiry VARCHAR(255), 
                price VARCHAR(50),
                sku VARCHAR(50),
                email VARCHAR(255),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (email) REFERENCES users(email) ON DELETE SET NULL
            )
        """)
    conn.commit()
    conn.close()

# Database connection function
def get_db_connection():
    return pymysql.connect(**DB_CONFIG)

# Gemini OCR logic
def extract_info_from_image(pil_image):
    try:
        response = model.generate_content(
            [
                "Extract product details and return ONLY a JSON object with keys: name, brand, product_type, size, expiry, price, sku.",
                pil_image
            ],
            generation_config={"temperature": 0.3, "top_p": 1, "top_k": 40, "max_output_tokens": 512},
            safety_settings={"HARASSMENT": "block_none", "HATE": "block_none", "SEXUAL": "block_none", "DANGEROUS": "block_none"},
        )

        raw_text = response.text.strip()
        match = re.search(r"\{[\s\S]*\}", raw_text)
        if match:
            return {"status": "success", "data": json.loads(match.group(0))}
        return {"status": "error", "message": "No valid JSON found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Insert product into DB
def insert_into_database(data):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO products (name, price, sku, expiry, brand, product_type, size, email)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            data["name"],
            data["price"],
            data["sku"],
            data["expiry"],
            data["brand"],
            data["product_type"],
            data["size"],
            data["email"]
        )

        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print("DB Insert Error:", e)
        return False

# Insert user into DB
def insert_user(user_data):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "INSERT INTO users (email, username, password) VALUES (%s, %s, %s)"
        cursor.execute(query, (user_data.email, user_data.username, user_data.password))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except pymysql.err.IntegrityError:
        return False
    except Exception as e:
        print("User Insert Error:", e)
        return False

# File Upload Endpoint
@app.post("/scan-image")
async def scan_image(file: UploadFile = File(...), email: str = ""):
    try:
        image_bytes = await file.read()
        pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        result = extract_info_from_image(pil_image)

        if result["status"] == "success":
            result["data"]["email"] = email
            success = insert_into_database(result["data"])
            if success:
                return {"message": "Product extracted and saved", "data": result["data"]}
            else:
                return {"message": "Data extracted but DB insert failed", "data": result["data"]}
        else:
            return {"message": "Extraction failed", "error": result["message"]}
    except Exception as e:
        return {"error": str(e)}

# Camera Capture Endpoint
@app.get("/capture")
def capture_image_and_extract(email: str = ""):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise HTTPException(status_code=500, detail="Failed to open camera")

    ret, frame = cap.read()
    cap.release()

    if not ret:
        raise HTTPException(status_code=500, detail="Failed to capture image")

    pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    result = extract_info_from_image(pil_image)

    if result["status"] == "success":
        result["data"]["email"] = email
        success = insert_into_database(result["data"])
        if success:
            return {"message": "Captured, extracted, and saved", "data": result["data"]}
        else:
            return {"message": "Captured & extracted, but DB insert failed", "data": result["data"]}
    else:
        raise HTTPException(status_code=500, detail=result["message"])

# Manual Add Product Endpoint
@app.post("/add_product")
async def add_product(product: Product):
    try:
        success = insert_into_database(product.dict())
        if success:
            return {"message": "✅ Product manually added"}
        else:
            raise HTTPException(status_code=500, detail="❌ DB insert failed")
    except ValueError:
        raise HTTPException(status_code=400, detail="❌ Invalid expiry date format. Use DD/MM/YY")

# Register/Login Endpoint
@app.post("/register")
def register_user(user: User):
    success = insert_user(user)
    if success:
        return {"message": "✅ User registered successfully"}
    else:
        raise HTTPException(status_code=400, detail="❌ User already exists or registration failed")

# On app startup
@app.on_event("startup")
def startup_event():
    setup_mysql()

# Host and port setup
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
