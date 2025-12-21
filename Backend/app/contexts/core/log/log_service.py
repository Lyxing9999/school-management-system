import logging
import sys
import json
import os
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
        self.logger.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())

        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter("%(message)s"))

        # Avoid double handlers in reload/debug
        if not self.logger.handlers:
            self.logger.addHandler(handler)

        # --- policy knobs ---
        self.pretty = os.getenv("LOG_PRETTY", "false").lower() in ("1", "true", "yes", "y")
        self.max_str = int(os.getenv("LOG_MAX_STR", "250"))
        self.max_depth = int(os.getenv("LOG_MAX_DEPTH", "5"))
        self.max_list = int(os.getenv("LOG_MAX_LIST", "50"))

        self.sensitive_keys = {
            "authorization", "cookie", "set-cookie",
            "password", "pass", "pwd",
            "token", "access_token", "refresh_token", "id_token",
            "jwt", "secret", "api_key", "apikey",
        }

        # If you pass request headers into extra, we will keep only these
        self.allowed_header_keys = {
            "host", "user-agent", "content-type", "accept",
            "origin", "referer",
            "x-request-id", "x-correlation-id", "x-forwarded-for",
        }

    # -------------------------
    # Sanitization helpers
    # -------------------------
    def _truncate(self, value: Any, max_len: Optional[int] = None) -> Any:
        if value is None:
            return None
        max_len = max_len or self.max_str
        s = value.decode("utf-8", "ignore") if isinstance(value, (bytes, bytearray)) else str(value)
        return s if len(s) <= max_len else s[:max_len] + "...(trunc)"

    def _sanitize_headers(self, headers: Dict[str, Any]) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        for k, v in headers.items():
            lk = str(k).lower()
            # hard-block common secrets
            if lk in ("authorization", "cookie", "set-cookie"):
                continue
            if lk in self.allowed_header_keys:
                out[k] = self._truncate(v, 200)
        return out

    def _sanitize(self, obj: Any, *, depth: int = 0) -> Any:
        """
        Recursively sanitize data for logs:
        - redact sensitive keys
        - truncate long strings
        - bound depth and list length
        """
        if obj is None:
            return None

        if depth >= self.max_depth:
            return "[TRUNCATED_DEPTH]"

        if isinstance(obj, dict):
            out: Dict[str, Any] = {}
            for k, v in obj.items():
                lk = str(k).lower()

                # redact sensitive keys anywhere
                if lk in self.sensitive_keys:
                    out[k] = "[REDACTED]"
                    continue

                # special-case headers if present
                if lk == "headers" and isinstance(v, dict):
                    out[k] = self._sanitize_headers(v)
                    continue

                out[k] = self._sanitize(v, depth=depth + 1)
            return out

        if isinstance(obj, list):
            trimmed = obj[: self.max_list]
            return [self._sanitize(x, depth=depth + 1) for x in trimmed] + (
                ["...(trunc_list)"] if len(obj) > self.max_list else []
            )

        if isinstance(obj, (str, bytes, bytearray)):
            return self._truncate(obj)

        # Convert basic non-JSON types safely
        if isinstance(obj, (int, float, bool)):
            return obj

        # Fallback string conversion for ObjectId/datetime/etc.
        return self._truncate(obj)

    # -------------------------
    # Main log method
    # -------------------------
    def log(
        self,
        message: str,
        level: str = "INFO",
        module: Optional[str] = None,
        user_id: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None
    ):
        log_data = {
            "ts": datetime.utcnow().isoformat(),
            "level": level.upper(),
            "module": module or "unknown",
            "user_id": user_id,
            "msg": self._truncate(message, 400),
            "extra": self._sanitize(extra or {}),
        }

        # Single-line JSON for monitoring systems (ELK/Loki/CloudWatch/etc.)
        payload = (
            json.dumps(log_data, indent=2, default=str)
            if self.pretty
            else json.dumps(log_data, separators=(",", ":"), default=str)
        )

        lvl = level.lower()
        if lvl == "info":
            self.logger.info(payload)
        elif lvl in ("warn", "warning"):
            self.logger.warning(payload)
        elif lvl == "error":
            self.logger.error(payload)
        elif lvl == "debug":
            self.logger.debug(payload)
        else:
            self.logger.info(payload)

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