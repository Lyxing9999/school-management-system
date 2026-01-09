import os
from typing import Optional, List
from urllib.parse import urlparse

from dotenv import load_dotenv

from app.contexts.core.errors.app_base_exception import handle_exception


def _parse_csv(value: str) -> List[str]:
    return [x.strip() for x in (value or "").split(",") if x.strip()]


def _normalize_origin(origin: str) -> str:
    """
    Normalize an origin to browser-expected form:
    - remove trailing slash
    - keep scheme://host[:port]
    """
    o = (origin or "").strip().rstrip("/")
    return o


def _is_valid_origin(origin: str) -> bool:
    """
    Very practical validation for CORS origins:
    - must be absolute URL with scheme http/https
    - must have netloc
    """
    try:
        u = urlparse(origin)
        if u.scheme not in ("http", "https"):
            return False
        if not u.netloc:
            return False
        # Browser Origin never includes path/query/fragment
        if u.path not in ("", "/"):
            return False
        if u.query or u.fragment:
            return False
        return True
    except Exception:
        return False


class Settings:
    def __init__(self):
        # Load .env only if present; keep it safe for prod (prod should use real env vars)
        load_dotenv()

        self.DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

        # Feature flags
        self.ENABLE_GOOGLE_OAUTH: bool = os.getenv("ENABLE_GOOGLE_OAUTH", "false").lower() == "true"

        # Core
        self.SECRET_KEY: str = os.getenv("SECRET_KEY", "")
        self.DATABASE_URI: str = os.getenv("DATABASE_URI", "mongodb://localhost:27017")

        # JWT
        self.ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
        self.JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")

        # Frontend
        self.FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000").strip().rstrip("/")

        # Google OAuth
        self.GOOGLE_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_CLIENT_ID")
        self.GOOGLE_CLIENT_SECRET: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET")
        self.GOOGLE_DISCOVERY_URL: str = "https://accounts.google.com/.well-known/openid-configuration"

        # Telegram
        self.TELEGRAM_BOT_TOKEN: Optional[str] = os.getenv("TELEGRAM_BOT_TOKEN")

        # CORS origins (exact origins only when credentials are enabled)
        raw_origins = os.getenv(
            "CORS_ALLOWED_ORIGINS",
            "http://localhost:3000,http://127.0.0.1:3000",
        )

        origins = [_normalize_origin(x) for x in _parse_csv(raw_origins)]
        # Always include frontend url if defined
        if self.FRONTEND_URL:
            origins.append(_normalize_origin(self.FRONTEND_URL))

        # De-duplicate while preserving order
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
        # 1) Production safety: secret key must exist in non-debug
        if not self.DEBUG and not self.SECRET_KEY:
            raise handle_exception(ValueError("SECRET_KEY must be set when DEBUG=false."))

        # 2) CORS origin validation (prevents silent browser failures)
        bad = [o for o in self.CORS_ALLOWED_ORIGINS if not _is_valid_origin(o)]
        if bad:
            raise handle_exception(ValueError(f"Invalid CORS origin(s): {bad}"))

        # 3) Google OAuth validation only when enabled
        if self.ENABLE_GOOGLE_OAUTH and (not self.GOOGLE_CLIENT_ID or not self.GOOGLE_CLIENT_SECRET):
            raise handle_exception(
                ValueError("GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set when ENABLE_GOOGLE_OAUTH=true.")
            )


settings = Settings()