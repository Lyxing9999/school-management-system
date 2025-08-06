from flask import g
from app.error.exceptions import UnauthorizedError, ErrorSeverity, ErrorCategory

def get_current_user_id() -> str:
    user = getattr(g, 'user', None)
    user_id = user.get("id") if isinstance(user, dict) else getattr(user, "id", None)
    
    if not user_id:
        raise UnauthorizedError(message="Unauthorized: User not found", user_message="You are not authorized to access this resource.", hint="Please login to continue.", status_code=401, severity=ErrorSeverity.HIGH, category=ErrorCategory.AUTHENTICATION)
    
    return user_id