from flask import request, g
import jwt
from app.contexts.core.config.setting import settings  # JWT secret and algorithm
from app.contexts.core.error import AppBaseException, ErrorSeverity, ErrorCategory

def get_current_user(role: str | None = None) -> dict:
    """
    Extracts the current user's ID and role from the JWT token in the Authorization header.
    Optionally enforces a specific role.
    
    Returns:
        dict: {"user_id": str, "role": str}
    
    Raises:
        AppBaseException if the token is missing, invalid, expired, or role does not match.
    """
    # Reuse cached user in g if available (prevents multiple JWT decodes per request)
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

    # Extract token from Authorization header
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
        # Decode JWT
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get("id")
        user_role = payload.get("role")

        if not user_id or not user_role:
            raise ValueError("User ID or role not found in token")

        # Enforce role if specified
        if role and user_role != role:
            raise AppBaseException(
                message=f"User role must be '{role}'",
                severity=ErrorSeverity.HIGH,
                category=ErrorCategory.AUTHENTICATION,
                status_code=403,
                user_message="Unauthorized role",
                recoverable=False
            )

        user = {"user_id": user_id, "role": user_role}
        g.current_user = user
        return user

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