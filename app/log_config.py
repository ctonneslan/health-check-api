import logging
import json
from app.middleware import get_request_id

# JSON log formatter
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "component": getattr(record, "component", None),
            "request_id": getattr(record, "request_id", get_request_id()),
        }

        if hasattr(record, "extra") and isinstance(record.extra, dict):
            log_record.update(record.extra)

        return json.dumps({k: v for k, v in log_record.items() if v is not None})

# Logger adapter that injects request_id
class RequestLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        extra = self.extra.copy()
        extra["request_id"] = get_request_id()
        if "extra" in kwargs:
            extra.update(kwargs["extra"])
        kwargs["extra"] = {"extra": extra}
        return msg, kwargs

# Create and configure logger
logger = logging.getLogger("health")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
logger.propagate = False

# Use adapter for request_id injection
logger = RequestLoggerAdapter(logger, {})
