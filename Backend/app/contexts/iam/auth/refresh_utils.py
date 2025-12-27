import secrets
import hashlib
from datetime import datetime, timedelta

from app.contexts.core.config.setting import settings 

REFRESH_TTL = timedelta(days=14)

REFRESH_PEPPER = getattr(settings, "REFRESH_PEPPER", settings.SECRET_KEY)

def create_refresh_token() -> str:
    return secrets.token_urlsafe(32)

def hash_refresh_token(token: str) -> str:
    return hashlib.sha256((token + REFRESH_PEPPER).encode("utf-8")).hexdigest()


def now_utc() -> datetime:
   
    return datetime.utcnow()