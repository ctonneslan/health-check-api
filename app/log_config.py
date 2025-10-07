import logging
import json
from datetime import datetime, timezone

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
        }

        # Include any extra fields passed to logger
        if hasattr(record, "extra"):
            log_record.update(record.extra)

        return json.dumps(log_record)
