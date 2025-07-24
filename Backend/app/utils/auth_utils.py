from flask import g
from app.error.exceptions import UnauthorizedError

def get_current_user_id() -> str:
    user = getattr(g, 'user', None)
    user_id = user.get("id") if isinstance(user, dict) else getattr(user, "id", None)
    
    if not user_id:
        raise UnauthorizedError(message="Unauthorized: User not found", status_code=401)
    
    return user_id