from fastapi import FastAPI
import random
import shutil

app = FastAPI()

# Add a /health route
@app.get("/health")
def health():
    return {}

# Database check
def check_database():
    if random.random() < 0.9:
        return "ok"
    else:
        return "fail"

# Disk usage
def check_disk_usage():
    total, used, free = shutil.disk_usage("/")
    usage_percent = used / total * 100

    if usage_percent < 70:
        return "ok"
    elif usage_percent < 90:
        return "warn"
    else:
        return "fail"
