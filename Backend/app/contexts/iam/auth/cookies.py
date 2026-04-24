from __future__ import annotations

from app.contexts.core.config.setting import settings
from app.contexts.iam.auth.refresh_utils import REFRESH_TTL

COOKIE_NAME = "refresh_token"


def _bool(v) -> bool:
    return bool(v) and str(v).lower() not in ("0", "false", "no", "off")


def set_refresh_cookie(resp, refresh_token: str):
    secure = _bool(getattr(settings, "COOKIE_SECURE", False))
    samesite = getattr(settings, "COOKIE_SAMESITE", "Lax")
    domain = getattr(settings, "COOKIE_DOMAIN", None)
    path = getattr(settings, "COOKIE_PATH", "/api/iam")

    # Browser rule: SameSite=None MUST be Secure (HTTPS)
    if str(samesite).lower() == "none" and not secure:
        raise ValueError("Invalid cookie config: SameSite=None requires Secure=True (HTTPS).")

    resp.set_cookie(
        COOKIE_NAME,
        refresh_token,
        httponly=True,
        secure=secure,
        samesite=samesite,     # "Lax" (dev) or "None" (prod cross-site)
        domain=domain,         # usually None for Render/Vercel different domains
        path=path,             # must match clear_refresh_cookie
        max_age=max(1, int(REFRESH_TTL.total_seconds())),
    )


def clear_refresh_cookie(resp):
    secure = _bool(getattr(settings, "COOKIE_SECURE", False))
    samesite = getattr(settings, "COOKIE_SAMESITE", "Lax")
    domain = getattr(settings, "COOKIE_DOMAIN", None)
    path = getattr(settings, "COOKIE_PATH", "/api/iam")

    resp.delete_cookie(
        COOKIE_NAME,
        domain=domain,
        path=path,
        secure=secure,
        samesite=samesite,
    )
