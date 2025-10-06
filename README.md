# Health Check API

This is a small FastAPI project that exposes a single `/health` endpoint.  
It checks the status of three components:

- A simulated PostgreSQL database connection
- Disk usage on the local machine
- An external API (Postman Echo)

The endpoint returns a status based on whether each component is healthy or not.

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/ctonneslan/health-check-api.git
cd health-check-api
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

## Running the app

### 1. Use uvicorn to run the FastAPI server:

```bash
uvicorn main:app --reload
```

## Exposing the endpoint

### 1. GET /health

Example Response:

```bash
curl http://localhost:8000/health
```

```json
{
  "status": "ok",
  "timestamp": "2025-10-06T23:10:41.000Z",
  "components": {
    "database": "ok",
    "disk_usage": "ok",
    "external_api": "ok"
  },
  "response_times_ms": {
    "database": 0.12,
    "disk_usage": 0.24,
    "external_api": 351.73
  }
}
```
