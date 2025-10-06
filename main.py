from fastapi import FastAPI
import random

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

