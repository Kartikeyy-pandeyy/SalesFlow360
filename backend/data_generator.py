# data_generator.py
import boto3
import json
import random
import time
from datetime import datetime, timedelta
from faker import Faker
import threading

fake = Faker()

# Shared data buffer
live_sales = []
buffer_lock = threading.Lock()  # For thread-safe operations

PRODUCT_CATALOG = [
    {"product_id": "PROD-101", "product_name": "Wireless Mouse", "unit_price": 500, "cost_price": 300},
    {"product_id": "PROD-102", "product_name": "Bluetooth Headphones", "unit_price": 1200, "cost_price": 800},
    {"product_id": "PROD-103", "product_name": "USB-C Cable", "unit_price": 300, "cost_price": 100},
    {"product_id": "PROD-104", "product_name": "Portable SSD", "unit_price": 3500, "cost_price": 2800},
    {"product_id": "PROD-105", "product_name": "Webcam 1080p", "unit_price": 1800, "cost_price": 1100},
    {"product_id": "PROD-106", "product_name": "Laptop Stand", "unit_price": 1500, "cost_price": 900},
    {"product_id": "PROD-107", "product_name": "Smartwatch", "unit_price": 4500, "cost_price": 3200},
    {"product_id": "PROD-108", "product_name": "Mechanical Keyboard", "unit_price": 2200, "cost_price": 1600},
    {"product_id": "PROD-109", "product_name": "Noise Cancelling Earbuds", "unit_price": 2600, "cost_price": 1800},
    {"product_id": "PROD-110", "product_name": "4K Monitor", "unit_price": 12000, "cost_price": 9000}
]

REGIONS = ["North", "South", "East", "West"]

BUCKET_NAME = "salesflow360"
s3 = boto3.client("s3")


def get_ist_time():
    return datetime.utcnow() + timedelta(hours=5, minutes=30)


def generate_sale():
    product = random.choice(PRODUCT_CATALOG)
    quantity = random.randint(1, 5)
    ist_now = get_ist_time()

    return {
        "order_id": f"ORD-{ist_now.strftime('%Y%m%d')}-{random.randint(1000, 9999)}",
        "product_id": product["product_id"],
        "product_name": product["product_name"],
        "region": random.choice(REGIONS),
        "order_date": ist_now.isoformat(),
        "unit_price": product["unit_price"],
        "cost_price": product["cost_price"],
        "quantity": quantity,
        "returned": random.choice([False, False, False, True])
    }


def generate_data_continuously():
    while True:
        sale = generate_sale()
        with buffer_lock:
            live_sales.append(sale)
        time.sleep(5)  # every 5 seconds


def upload_sales_to_s3():
    while True:
        time.sleep(1800)  # every 30 minutes

        with buffer_lock:
            data_to_upload = live_sales.copy()
            live_sales.clear()

        if not data_to_upload:
            print("[⚠️ S3 SKIP] No data to upload this cycle.")
            continue

        timestamp = get_ist_time().strftime("%Y-%m-%dT%H-%M-%S")
        filename = f"sales_data_{timestamp}.json"

        try:
            s3.put_object(
                Bucket=BUCKET_NAME,
                Key=f"sales/{filename}",
                Body=json.dumps(data_to_upload, indent=2),
                ContentType="application/json"
            )
            print(f"[✅ S3 UPLOAD] {len(data_to_upload)} records → {filename}")
        except Exception as e:
            print(f"[❌ S3 ERROR] Upload failed: {e}")
