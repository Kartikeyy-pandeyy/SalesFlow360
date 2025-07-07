# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import threading
from data_generator import generate_data_continuously, upload_sales_to_s3, live_sales, buffer_lock

# Define the new FastAPI lifespan handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🔁 Starting data generator and S3 uploader (lifespan)...")
    threading.Thread(target=generate_data_continuously, daemon=True).start()
    threading.Thread(target=upload_sales_to_s3, daemon=True).start()
    yield  # Startup complete
    # No cleanup needed on shutdown for now

# Pass lifespan handler to the app
app = FastAPI(lifespan=lifespan)

# Allow frontend (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all during dev; restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route to get last 5 sales
@app.get("/sales")
def get_recent_sales():
    with buffer_lock:
        recent = live_sales[-5:]
    return {"sales": recent}

# Route to get entire 30-minute buffer
@app.get("/buffer")
def get_full_buffer():
    with buffer_lock:
        buffer_copy = live_sales.copy()
    return {"buffer": buffer_copy}
