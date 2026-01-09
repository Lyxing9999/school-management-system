from __future__ import annotations
from app.contexts.core.config.setting import settings

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
        # In production, this should be treated as misconfig.
        # In dev, you should not use None.
        raise ValueError("Invalid cookie config: SameSite=None requires Secure=True (HTTPS).")

    resp.set_cookie(
        COOKIE_NAME,
        refresh_token,
        httponly=True,
        secure=secure,
        samesite=samesite,       # "Lax" (dev) or "None" (prod cross-site)
        domain=domain,           # None is fine for same host; use ".domain.com" for subdomains
        path=path,               # must match clear_refresh_cookie
        max_age=14 * 24 * 3600,
    )


def clear_refresh_cookie(resp):
    secure = _bool(getattr(settings, "COOKIE_SECURE", False))
    samesite = getattr(settings, "COOKIE_SAMESITE", "Lax")
    domain = getattr(settings, "COOKIE_DOMAIN", None)
    path = getattr(settings, "COOKIE_PATH", "/api/iam")

    # Deleting cookies must match attributes (path/domain)
    resp.delete_cookie(
        COOKIE_NAME,
        domain=domain,
        path=path,
        secure=secure,
        samesite=samesite,
    )