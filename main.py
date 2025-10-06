from fastapi import FastAPI, Response
import random
import shutil
import httpx
import logging
import json
from datetime import datetime
import os
from dotenv import load_dotenv

# Load variables from .env
load_dotenv() 

EXTERNAL_API_URL = os.getenv("EXTERNAL_API_URL", "https://postman-echo.com/status/200")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

app = FastAPI()

# Add a /health route
@app.get("/health")
async def health():
    db = check_database()
    disk = check_disk_usage()
    api = await check_external_api()

    if db != "ok":
        logger.warning(f"Database check status: {db}")
    if disk != "ok":
        logger.warning(f"Disk usage status: {disk}")
    if api != "ok":
        logger.warning(f"External API check failed with status: {api}")

    statuses = {db, disk, api}
    status = ""
    if "fail" in statuses:
        status = "fail"
    elif "warn" in statuses:
        status = "warn"
    else:
        status = "ok"
    
    logger.info(f"Overall health status: {status}")

    timestamp = datetime.utcnow().isoformat() + 'Z'

    return Response(
        content=json.dumps({
            "status": status,
            "timestamp": timestamp,
            "components": {
                "database": db,
                "disk_usage": disk,
                "external_api": api
            }
        }),
        media_type="application/json",
        status_code=503 if status == "fail" else 200
    )

# 1. Database Check
def check_database():
    if random.random() < 0.9:
        return "ok"
    else:
        return "fail"

# 2. Disk Usage Check
def check_disk_usage():
    total, used, free = shutil.disk_usage("/")
    usage_percent = used / total * 100

    if usage_percent < 70:
        return "ok"
    elif usage_percent < 90:
        return "warn"
    else:
        return "fail"
    
# 3. External API Check
async def check_external_api():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(EXTERNAL_API_URL)
            return "ok" if response.status_code == 200 else "fail"
    except Exception as e:
        logger.error(f"External API check error: {e}")
        return "fail"