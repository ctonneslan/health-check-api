from fastapi import FastAPI
import random
import shutil
import httpx

app = FastAPI()

# Add a /health route
@app.get("/health")
def health():
    return {}

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
            response = await client.get("https://postman-echo.com/status/200")
            return "ok" if response.status_code == 200 else "fail"
    except:
        return "fail"