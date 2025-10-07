from fastapi import FastAPI, Response, Query
import logging
import json
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv
import time
from app.health_checks import check_database, check_disk_usage, check_external_api
from app.log_config import JSONFormatter

# Track when app starts
app_start_time = datetime.now(timezone.utc)

# Load variables from .env
load_dotenv() 

SLOW_RESPONSE_THRESHOLD_MS = {
    "database": int(os.getenv("SLOW_DB_MS", "100")),
    "disk_usage": int(os.getenv("SLOW_DISK_MS", "50")),
    "external_api": int(os.getenv("SLOW_EXTERNAL_API_MS", "300")),
}

handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(handler)
logger.propagate = False


logger = logging.getLogger(__name__)

app = FastAPI()

# Add a /health route
@app.get("/health")
async def health(details: bool = Query(default=True, description="Include full health details")):
    # Database check
    t0 = time.perf_counter()
    db = check_database()
    db_time = (time.perf_counter() - t0) * 1000
    logger.info("Database check", extra={"extra": {
        "component": "database", "status": db, "duration_ms": round(db_time, 2)
    }})
    if db_time > SLOW_RESPONSE_THRESHOLD_MS["database"]:
        logger.warning(f"Database check slow: {db_time:.2f} ms")

    # Disk usage check
    t0 = time.perf_counter()
    disk = check_disk_usage()
    disk_time = (time.perf_counter() - t0) * 1000
    logger.info("Disk usage check", extra={"extra": {
        "component": "disk_usage", "status": disk, "duration_ms": round(disk_time, 2)
    }})
    if disk_time > SLOW_RESPONSE_THRESHOLD_MS["disk_usage"]:
        logger.warning(f"Disk usage check slow: {disk_time:.2f} ms")
    
    # External API check
    t0 = time.perf_counter()
    api = await check_external_api()
    api_time = (time.perf_counter() - t0) * 1000
    logger.info("External API check", extra={"extra": {
        "component": "api", "status": api, "duration_ms": round(api_time, 2)
    }})
    if api_time > SLOW_RESPONSE_THRESHOLD_MS["external_api"]:
        logger.warning(f"External API check slow: {api_time:.2f} ms")

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

    # Include timestamp and uptime
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    uptime_delta = datetime.now(timezone.utc) - app_start_time
    uptime_str = str(timedelta(seconds=int(uptime_delta.total_seconds())))

    response_body = {
        "status": status
    }

    if details:
        response_body.update({
            "timestamp": timestamp,
            "uptime": uptime_str,
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
        })

    return Response(
        content=json.dumps(response_body),
        media_type="application/json",
        status_code=503 if status == "fail" else 200
    )
