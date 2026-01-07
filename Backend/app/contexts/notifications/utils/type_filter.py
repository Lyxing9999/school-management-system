from typing import Optional
from flask import request
from app.contexts.notifications.types import NotifType 
def parse_type_filter() -> Optional[str]:
    t = request.args.get("type")
    if not t:
        return None
    t = str(t).strip()
    if t not in NotifType.all():
        # raise a ValueError and let wrap_response convert to 400,
        # or return None if you prefer "ignore invalid"
        raise ValueError(f"Invalid notification type: {t}")
    return t

def parse_unread_only() -> bool:
    v = str(request.args.get("unread_only") or "").lower().strip()
    return v in ("1", "true", "yes", "y")