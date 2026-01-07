import secrets
import hashlib
from datetime import datetime, timedelta

from app.contexts.core.config.setting import settings

RESET_TTL = timedelta(minutes=30)
RESET_PEPPER = getattr(settings, "RESET_PEPPER", settings.SECRET_KEY)

def create_reset_token() -> str:
    return secrets.token_urlsafe(32)

def hash_reset_token(token: str) -> str:
    return hashlib.sha256((token + RESET_PEPPER).encode("utf-8")).hexdigest()

def now_utc() -> datetime:
    return datetime.utcnow()