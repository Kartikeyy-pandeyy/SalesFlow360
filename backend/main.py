# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import threading
from data_generator import generate_data_continuously, upload_sales_to_s3, live_sales, buffer_lock

app = FastAPI()

# CORS setup to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to specific domains in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/sales")
def get_recent_sales():
    with buffer_lock:
        recent = live_sales[-5:]
    return {"sales": recent}

@app.get("/buffer")
def get_full_buffer():
    with buffer_lock:
        buffer_copy = live_sales.copy()
    return {"buffer": buffer_copy}

@app.on_event("startup")
def start_background_threads():
    print("🔁 Starting data generator and S3 uploader...")
    threading.Thread(target=generate_data_continuously, daemon=True).start()
    threading.Thread(target=upload_sales_to_s3, daemon=True).start()
