## Design Decisions and Iterative Process

This section outlines the decisions made while building the Health Check API, why they were made, and what tradeoffs were considered. It also includes ideas for further improvement if more time were available.

---

### Initial Requirements

The prompt asked for a single `/health` endpoint that:

- Checks the status of a simulated database
- Inspects disk usage health
- Pings an external API
- Returns a JSON response reflecting the overall health status

---

### Iterative Enhancements

Each improvement was added one step at a time to keep the design clear and extensible.

---

### 1. **Basic Health Checks**

**Why:** Start with core logic to ensure each system (DB, disk, external API) can return a health status.

- Simulated PostgreSQL check using try / except
- Disk check using `shutil.disk_usage`
- External API check using `httpx.AsyncClient`

**Tradeoffs:** The database check is mocked to avoid requiring a real DB — this keeps the app portable and testable.

---

### 2. **Structured Logging in JSON**

**Why:** To make logs machine-parsable and observability-friendly.

- Custom `JSONFormatter` for logs
- Consistent structure with `timestamp`, `level`, `message`, `component`, etc.

**Tradeoffs:** More verbose setup, but higher long-term maintainability.

---

### 3. **Request ID Tracing**

**Why:** Improves traceability across systems and logs, especially in concurrent or multi-user environments.

- Middleware injects a unique `request_id` per request
- Log entries and `/health` response both include the `request_id`

**Tradeoffs:** Slight increase in overhead, but significantly improves debugging in production.

---

### 4. **Optional Detail in Response**

**Why:** Some consumers may only care about the overall status, not the detailed breakdown.

- `GET /health?details=false` returns minimal payload
- Full payload remains default behavior

**Tradeoffs:** Minor logic branching in the endpoint, but offers flexibility to API consumers.

---

### 5. **Prometheus Metrics Integration**

**Why:** Enables operational observability via Prometheus dashboards.

- `/metrics` exposes:
  - Health check counters
  - Response time histograms
  - App uptime gauge
- Standardized with Prometheus naming conventions

**Tradeoffs:** Added one dependency (`prometheus_client`) and some in-memory storage.

---

### 6. **Performance Threshold Logging**

**Why:** Slow responses may indicate deeper problems, even if the check returns `"ok"`.

- Configurable thresholds via env vars:
  - `SLOW_DB_MS`
  - `SLOW_DISK_MS`
  - `SLOW_EXTERNAL_API_MS`
- Warnings are logged if a check exceeds its threshold

**Tradeoffs:** Manual tuning required for thresholds, but helpful for early performance alerts.

---

### Testing

- Unit tests written using `pytest` and `pytest-asyncio`
- Mocked disk usage and API responses
- Simulated DB behavior to test both `"ok"` and `"fail"`

---

## If More Time Was Available

### Security

- API key or token protection on `/health` and `/metrics`
- Rate limiting or CAPTCHA for public endpoints

### UI Dashboard

- A small frontend to visualize health in real-time
- Color-coded status and sparkline charts for metrics

### Real Database Support

- Optional integration with a real PostgreSQL server
- Retry logic and better error categorization

### Persisted Metrics / Logs

- Push metrics to a remote Prometheus instance
- Send logs to a centralized system (e.g., Loki or Logstash)

### Retry or Graceful Degradation

- Retry external API checks before failing
- Cache last known "good" state in case of flaky checks

---
