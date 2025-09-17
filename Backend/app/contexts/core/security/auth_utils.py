from flask import request, g
import jwt
from app.contexts.core.config.setting import settings
from app.contexts.core.error import AppBaseException, ErrorSeverity, ErrorCategory

# -----------------------------
# Get current user ID only
# -----------------------------
def get_current_user_id() -> str:
    if hasattr(g, "current_user_id"):
        return g.current_user_id

    user = _decode_jwt()
    g.current_user_id = user["user_id"]
    return g.current_user_id

# -----------------------------
# Get full current user info
# -----------------------------
def get_current_user(role: str | None = None) -> dict:
    if hasattr(g, "current_user"):
        user = g.current_user
        if role and user["role"] != role:
            raise AppBaseException(
                message=f"User role must be '{role}'",
                severity=ErrorSeverity.HIGH,
                category=ErrorCategory.AUTHENTICATION,
                status_code=403,
                user_message="Unauthorized role",
                recoverable=False
            )
        return user

    user = _decode_jwt()
    if role and user["role"] != role:
        raise AppBaseException(
            message=f"User role must be '{role}'",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.AUTHENTICATION,
            status_code=403,
            user_message="Unauthorized role",
            recoverable=False
        )

    g.current_user = user
    return user

# -----------------------------
# Internal helper to decode JWT
# -----------------------------
def _decode_jwt() -> dict:
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise AppBaseException(
            message="Authorization header missing",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.AUTHENTICATION,
            status_code=401,
            user_message="You must be logged in",
            recoverable=False
        )

    try:
        token_type, token = auth_header.split()
        if token_type.lower() != "bearer":
            raise ValueError("Invalid token type")
    except ValueError:
        raise AppBaseException(
            message="Invalid Authorization header format",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.AUTHENTICATION,
            status_code=401,
            user_message="Invalid authentication credentials",
            recoverable=False
        )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get("id")
        user_role = payload.get("role")
        if not user_id or not user_role:
            raise ValueError("User ID or role missing in token")
        return {"user_id": user_id, "role": user_role}
    except jwt.ExpiredSignatureError:
        raise AppBaseException(
            message="JWT token expired",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.AUTHENTICATION,
            status_code=401,
            user_message="Session expired. Please log in again",
            recoverable=False
        )
    except jwt.InvalidTokenError as e:
        raise AppBaseException.from_exception(
            e,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.AUTHENTICATION,
            status_code=401,
            user_message="Invalid authentication credentials",
            recoverable=False
        )