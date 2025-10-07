import shutil
import httpx
import logging
from unittest import mock
import os

# Setup logging
logger = logging.getLogger(__name__)

EXTERNAL_API_URL = os.getenv("EXTERNAL_API_URL", "https://postman-echo.com/status/200")
DISK_WARN_THRESHOLD = int(os.getenv("DISK_WARN_THRESHOLD", "70"))
DISK_FAIL_THRESHOLD = int(os.getenv("DISK_FAIL_THRESHOLD", "90"))

# 1. Database Check
def check_database():
    try:
        if simulate_db_connection():
            return "ok"
        else:
            return "fail"
    except Exception as e:
        logger.warning(f"Database simulation error: {e}")
        return "fail"

def simulate_db_connection():
    """
    Simulate a DB connection. Can be toggled to always succeed or fail,
    or replaced with real logic later.
    """
    # Change this return value manually to simulate failure or success
    return True

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