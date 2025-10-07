from fastapi import FastAPI, Response
import random
import shutil
import httpx
import logging
import json
from datetime import datetime
import os
from dotenv import load_dotenv
import time

# Load variables from .env
load_dotenv() 

EXTERNAL_API_URL = os.getenv("EXTERNAL_API_URL", "https://postman-echo.com/status/200")
DISK_WARN_THRESHOLD = int(os.getenv("DISK_WARN_THRESHOLD", "70"))
DISK_FAIL_THRESHOLD = int(os.getenv("DISK_FAIL_THRESHOLD", "90"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

app = FastAPI()

# Add a /health route
@app.get("/health")
async def health():
    # Database check
    t0 = time.perf_counter()
    db = check_database()
    db_time = (time.perf_counter() - t0) * 1000
    logger.info(f"Database check took {db_time:.2f} ms")

    # Disk usage check
    t0 = time.perf_counter()
    disk = check_disk_usage()
    disk_time = (time.perf_counter() - t0) * 1000
    logger.info(f"Disk usage check took {disk_time:.2f} ms")
    
    # External API check
    t0 = time.perf_counter()
    api = await check_external_api()
    api_time = (time.perf_counter() - t0) * 1000
    logger.info(f"External API check took {api_time:.2f} ms")

    # Log component status levels
    if db != "ok":
        logger.warning(f"Database check status: {db}")
    if disk != "ok":
        logger.warning(f"Disk usage status: {disk}")
    if api != "ok":
        logger.warning(f"External API check failed with status: {api}")

    # Determine overall health status
    statuses = {db, disk, api}
    status = ""
    if "fail" in statuses:
        status = "fail"
    elif "warn" in statuses:
        status = "warn"
    else:
        status = "ok"
    
    logger.info(f"Overall health status: {status}")

    # Include timestamp
    timestamp = datetime.utcnow().isoformat() + 'Z'

    return Response(
        content=json.dumps({
            "status": status,
            "timestamp": timestamp,
            "components": {
                "database": db,
                "disk_usage": disk,
                "external_api": api
            },
            "response_times_ms": {
                "database": round(db_time, 2),
                "disk_usage": round(disk_time, 2),
                "external_api": round(api_time, 2)
            }
        }),
        media_type="application/json",
        status_code=503 if status == "fail" else 200
    )

# 1. Database Check
def check_database():
    try:
        if random.choice([True, False]):
            return "ok"
        else:
            raise Exception("Simulated failure")
    except Exception:
        return "fail"

# 2. Disk Usage Check
def check_disk_usage():
    total, used, free = shutil.disk_usage("/")
    usage_percent = used / total * 100

    if usage_percent >= DISK_FAIL_THRESHOLD:
        return "fail"
    elif usage_percent >= DISK_WARN_THRESHOLD:
        return "warn"
    else:
        return "ok"
    
# 3. External API Check
async def check_external_api():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(EXTERNAL_API_URL)
            return "ok" if response.status_code == 200 else "fail"
    except Exception as e:
        logger.error(f"External API check error: {e}")
        return "fail"