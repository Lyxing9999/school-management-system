import os
from typing import Optional, List
from urllib.parse import urlparse

from dotenv import load_dotenv
from app.contexts.core.errors.app_base_exception import handle_exception


def _parse_csv(value: str) -> List[str]:
    return [x.strip() for x in (value or "").split(",") if x.strip()]


def _normalize_origin(origin: str) -> str:
    return (origin or "").strip().rstrip("/")


def _is_valid_origin(origin: str) -> bool:
    try:
        u = urlparse(origin)
        if u.scheme not in ("http", "https"):
            return False
        if not u.netloc:
            return False
        if u.path not in ("", "/"):
            return False
        if u.query or u.fragment:
            return False
        return True
    except Exception:
        return False


class Settings:
    def __init__(self):
        # Loads .env locally; in production you should set real env vars
        load_dotenv()

        self.DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
        self.ENABLE_GOOGLE_OAUTH: bool = os.getenv("ENABLE_GOOGLE_OAUTH", "false").lower() == "true"

        # Core
        self.SECRET_KEY: str = os.getenv("SECRET_KEY", "")
        self.DATABASE_URI: str = os.getenv("DATABASE_URI", "mongodb://localhost:27017")

        # JWT
        self.ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
        self.JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")

        # Frontend
        self.FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000").strip().rstrip("/")

        # Cookie config (IMPORTANT for prod)
        self.COOKIE_SECURE: str = os.getenv("COOKIE_SECURE", "false")  # string; cookies.py converts to bool
        self.COOKIE_SAMESITE: str = os.getenv("COOKIE_SAMESITE", "Lax")
        self.COOKIE_DOMAIN: Optional[str] = os.getenv("COOKIE_DOMAIN") or None
        self.COOKIE_PATH: str = os.getenv("COOKIE_PATH", "/api/iam")

        # Google OAuth
        self.GOOGLE_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_CLIENT_ID")
        self.GOOGLE_CLIENT_SECRET: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET")
        self.GOOGLE_DISCOVERY_URL: str = "https://accounts.google.com/.well-known/openid-configuration"

        # Telegram
        self.TELEGRAM_BOT_TOKEN: Optional[str] = os.getenv("TELEGRAM_BOT_TOKEN")

        # CORS
        raw_origins = os.getenv(
            "CORS_ALLOWED_ORIGINS",
            "http://localhost:3000,http://127.0.0.1:3000",
        )
        origins = [_normalize_origin(x) for x in _parse_csv(raw_origins)]

        if self.FRONTEND_URL:
            origins.append(_normalize_origin(self.FRONTEND_URL))

        # de-dupe
        seen = set()
        clean: List[str] = []
        for o in origins:
            if not o or o in seen:
                continue
            seen.add(o)
            clean.append(o)

        self.CORS_ALLOWED_ORIGINS = clean

        self._validate()

    def _validate(self):
        if not self.DEBUG and not self.SECRET_KEY:
            raise handle_exception(ValueError("SECRET_KEY must be set when DEBUG=false."))

        bad = [o for o in self.CORS_ALLOWED_ORIGINS if not _is_valid_origin(o)]
        if bad:
            raise handle_exception(ValueError(f"Invalid CORS origin(s): {bad}"))

        if self.ENABLE_GOOGLE_OAUTH and (not self.GOOGLE_CLIENT_ID or not self.GOOGLE_CLIENT_SECRET):
            raise handle_exception(
                ValueError("GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set when ENABLE_GOOGLE_OAUTH=true.")
            )


settings = Settings()