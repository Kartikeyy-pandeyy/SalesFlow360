from fastapi import FastAPI
from data_generator import live_sales, generate_data_continuously
from s3_uploader import upload_sales_to_s3
from threading import Thread
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SalesFlow360 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "SalesFlow360 is running with 30-min S3 batch uploads."}

@app.get("/sales")
def get_sales():
    return {"sales": live_sales[-100:]}  # Show last 100 records

from data_generator import live_sales

@app.get("/buffer")
def get_buffer_data():
    return {"buffer": live_sales.copy()}  # simulate buffer with current live data

@app.on_event("startup")
def start_background_tasks():
    Thread(target=generate_data_continuously, daemon=True).start()
    Thread(target=upload_sales_to_s3, daemon=True).start()
