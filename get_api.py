
from fastapi import FastAPI, HTTPException
import pymysql

app = FastAPI()

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "ritik@01A",
    "database": "scanner"
}

def get_db_connection():
    return pymysql.connect(**DB_CONFIG)

@app.get("/product-history")
def get_product_history():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products ORDER BY id DESC")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        keys = ["id", "name", "brand", "product_type", "size", "expiry", "price", "sku"]
        data = [dict(zip(keys, row)) for row in rows]

        return {"status": "success", "data": data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve product history: {str(e)}")
