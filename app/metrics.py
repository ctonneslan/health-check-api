from prometheus_client import Counter, Histogram, Gauge

# Counters for health check status by component
db_check_counter = Counter("healthcheck_database_total", "Number of database health checks", ["status"])
disk_check_counter = Counter("healthcheck_disk_usage_total", "Number of disk usage health checks", ["status"])
api_check_counter = Counter("healthcheck_external_api_total", "Number of external API health checks", ["status"])

# Histogram for response times in seconds
db_response_histogram = Histogram("healthcheck_database_response_seconds", "Database health check response time")
disk_response_histogram = Histogram("healthcheck_disk_usage_response_seconds", "Disk usage health check response time")
api_response_histogram = Histogram("healthcheck_external_api_response_seconds", "External API health check response time")

# Uptime gauge (seconds)
app_uptime_gauge = Gauge("app_uptime_seconds", "Application uptime in seconds")
