import logging
import sys
from datetime import datetime
from typing import Optional, Dict, Any

class LogService:
    _instance = None

    @staticmethod
    def get_instance() -> "LogService":
        if LogService._instance is None:
            LogService()
        return LogService._instance

    def __init__(self):
        if LogService._instance is not None:
            raise Exception("LogService is a singleton!")
        LogService._instance = self

        # Configure root logger
        self.logger = logging.getLogger("SchoolManagementSystem")
        self.logger.setLevel(logging.INFO)

        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "module": "%(name)s", "message": %(message)s}'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def log(
        self,
        message: str,
        level: str = "INFO",
        module: Optional[str] = None,
        user_id: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None
    ):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level.upper(),
            "module": module or "unknown",
            "user_id": user_id,
            "message": message,
            "extra": extra or {}
        }

        # Dispatch to proper logging method
        level_lower = level.lower()
        if level_lower == "info":
            self.logger.info(log_data)
        elif level_lower in ["warn", "warning"]:
            self.logger.warning(log_data)
        elif level_lower == "error":
            self.logger.error(log_data)
        elif level_lower == "debug":
            self.logger.debug(log_data)
        else:
            self.logger.info(log_data)

    # Convenience methods
    def info(self, message: str, **kwargs):
        self.log(message, level="INFO", **kwargs)

    def warn(self, message: str, **kwargs):
        self.log(message, level="WARN", **kwargs)

    def warning(self, message: str, **kwargs):
        self.log(message, level="WARN", **kwargs)

    def error(self, message: str, **kwargs):
        self.log(message, level="ERROR", **kwargs)

    def debug(self, message: str, **kwargs):
        self.log(message, level="DEBUG", **kwargs)

# Usage:
# log = LogService.get_instance()
# log.info("This is an info message", module="IAM", user_id="123")
# log.error("This is an error", extra={"payload": {...}})