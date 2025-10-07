from fastapi import FastAPI, Response, Query
import logging
import json
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv
import time
from time import perf_counter
from app.health_checks import check_database, check_disk_usage, check_external_api
from app.log_config import logger
from app.middleware import RequestIDMiddleware, get_request_id
from app.metrics import (
    db_check_counter, disk_check_counter, api_check_counter,
    db_response_histogram, disk_response_histogram, api_response_histogram,
    app_uptime_gauge
)
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response as FastAPIResponse

# Track when app starts
app_start_time = datetime.now(timezone.utc)

# Load variables from .env
load_dotenv() 

SLOW_RESPONSE_THRESHOLD_MS = {
    "database": int(os.getenv("SLOW_DB_MS", "100")),
    "disk_usage": int(os.getenv("SLOW_DISK_MS", "50")),
    "external_api": int(os.getenv("SLOW_EXTERNAL_API_MS", "300")),
}

app = FastAPI()
app.add_middleware(RequestIDMiddleware)

# Add a /health endpoint
@app.get("/health")
async def health(details: bool = Query(default=True, description="Include full health details")):
    # Database check
    t0 = perf_counter()
    with db_response_histogram.time():
        db = check_database()
    db_time = (perf_counter() - t0) * 1000
    db_check_counter.labels(status=db).inc()

    logger.info("Database check", extra={"extra": {
        "component": "database", "status": db, "duration_ms": round(db_time, 2)
    }})
    if db_time > SLOW_RESPONSE_THRESHOLD_MS["database"]:
        logger.warning(f"Database check slow: {db_time:.2f} ms")

    # Disk usage check
    t0 = perf_counter()
    with disk_response_histogram.time():
        disk = check_disk_usage()
    disk_time = (perf_counter() - t0) * 1000
    disk_check_counter.labels(status=disk).inc()

    logger.info("Disk usage check", extra={"extra": {
        "component": "disk_usage", "status": disk, "duration_ms": round(disk_time, 2)
    }})
    if disk_time > SLOW_RESPONSE_THRESHOLD_MS["disk_usage"]:
        logger.warning(f"Disk usage check slow: {disk_time:.2f} ms")
    
    # External API check
    t0 = perf_counter()
    with api_response_histogram.time():
        api = await check_external_api()
    api_time = (perf_counter() - t0) * 1000
    api_check_counter.labels(status=api).inc()

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
    app_uptime_gauge.set(uptime_delta.total_seconds())

    response_body = {
        "status": status,
        "request_id": get_request_id()
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

# Add a /metrics endpoint
@app.get("/metrics")
def metrics():
    return FastAPIResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)
