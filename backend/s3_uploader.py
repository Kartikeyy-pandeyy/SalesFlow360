import boto3
import json
import time
from datetime import datetime
from data_generator import live_sales, upload_buffer

s3 = boto3.client("s3")
BUCKET_NAME = "salesflow360"

def upload_sales_to_s3():
    while True:
        time.sleep(1800)  # 30 minutes

        # Step 1: Copy current buffer
        data_to_upload = live_sales.copy()

        # Step 2: Clear live buffer safely
        live_sales.clear()

        if not data_to_upload:
            print("[S3 SKIP] No data to upload this cycle.")
            continue

        # Step 3: Upload to S3
        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%S")
        filename = f"sales_data_{timestamp}.json"

        try:
            s3.put_object(
                Bucket=BUCKET_NAME,
                Key=f"sales/{filename}",
                Body=json.dumps(data_to_upload),
                ContentType="application/json"
            )
            print(f"[✅ S3 UPLOAD] {len(data_to_upload)} records → {filename}")
        except Exception as e:
            print(f"[❌ S3 ERROR] Upload failed: {e}")
