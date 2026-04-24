import secrets
import hashlib
from datetime import datetime, timedelta

from app.contexts.shared.time_utils import utc_now

from app.contexts.core.config.setting import settings 

def _refresh_ttl_days() -> int:
    raw = getattr(settings, "REFRESH_TOKEN_EXPIRE_DAYS", 14)
    try:
        days = int(raw)
    except (TypeError, ValueError):
        return 14
    return days if days > 0 else 14


REFRESH_TTL = timedelta(days=_refresh_ttl_days())

REFRESH_PEPPER = getattr(settings, "REFRESH_PEPPER", settings.SECRET_KEY)

def create_refresh_token() -> str:
    return secrets.token_urlsafe(32)

def hash_refresh_token(token: str) -> str:
    return hashlib.sha256((token + REFRESH_PEPPER).encode("utf-8")).hexdigest()


def now_utc() -> datetime:
    return utc_now()
