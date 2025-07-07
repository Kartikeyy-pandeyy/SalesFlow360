from faker import Faker
import random
from datetime import datetime
import threading
import time

fake = Faker()

live_sales = []       # Real-time data buffer
upload_buffer = []    # 30-min snapshot for upload

PRODUCT_CATALOG = [
    {"product_id": "PROD-101", "product_name": "Wireless Mouse", "unit_price": 500, "cost_price": 300},
    {"product_id": "PROD-102", "product_name": "Bluetooth Headphones", "unit_price": 1200, "cost_price": 800},
    {"product_id": "PROD-103", "product_name": "USB-C Cable", "unit_price": 300, "cost_price": 100},
    {"product_id": "PROD-104", "product_name": "Portable SSD", "unit_price": 3500, "cost_price": 2800},
    {"product_id": "PROD-105", "product_name": "Webcam 1080p", "unit_price": 1800, "cost_price": 1100}
]

REGIONS = ["North", "South", "East", "West"]

def generate_sale():
    product = random.choice(PRODUCT_CATALOG)
    quantity = random.randint(1, 5)
    return {
        "order_id": f"ORD-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000,9999)}",
        "product_id": product["product_id"],
        "product_name": product["product_name"],
        "region": random.choice(REGIONS),
        "order_date": datetime.utcnow().isoformat(),
        "unit_price": product["unit_price"],
        "cost_price": product["cost_price"],
        "quantity": quantity,
        "returned": random.choice([False, False, False, True])
    }

def generate_data_continuously():
    while True:
        sale = generate_sale()
        live_sales.append(sale)
        time.sleep(5)  # generate every 5 seconds
