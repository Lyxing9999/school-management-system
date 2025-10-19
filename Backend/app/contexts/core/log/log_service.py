import logging
import sys
import json
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

        self.logger = logging.getLogger("SchoolManagementSystem")
        self.logger.setLevel(logging.INFO)

        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter("%(message)s"))
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

        pretty_log = json.dumps(log_data, indent=2, default=str)
        level_lower = level.lower()

        if level_lower == "info":
            self.logger.info(pretty_log)
        elif level_lower in ["warn", "warning"]:
            self.logger.warning(pretty_log)
        elif level_lower == "error":
            self.logger.error(pretty_log)
        elif level_lower == "debug":
            self.logger.debug(pretty_log)
        else:
            self.logger.info(pretty_log)

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