from flask import request, g
import jwt
from bson.objectid import ObjectId

from app.contexts.core.config.setting import settings
from app.contexts.core.error import AppBaseException, ErrorSeverity, ErrorCategory
from app.contexts.shared.model_converter import mongo_converter


# -----------------------------
# Get current user ID (IAM._id as string)
# -----------------------------
def get_current_user_id() -> str:
    if hasattr(g, "current_user_id"):
        return g.current_user_id

    user = _decode_jwt()              # {"user_id": "<string>", "role": "..."}
    g.current_user_id = user["user_id"]
    return g.current_user_id


# -----------------------------
# Get current user ID as ObjectId (IAM._id)
# -----------------------------
def get_current_user_oid() -> ObjectId:
    """
    Return current IAM user id as ObjectId.
    """
    user_id_str = get_current_user_id()
    return mongo_converter.convert_to_object_id(user_id_str)


# -----------------------------
# Get current staff ID (staff._id)
# -----------------------------
def get_current_staff_id() -> ObjectId:
    """
    Resolve the current logged-in user (IAM) to their staff document and
    return staff._id.

    Used for teacher/ staff domain: schedules, classes, attendance, etc.
    """
    # 1) IAM user ObjectId
    user_oid = get_current_user_oid()

    # 2) Find staff by user_id
    staff_doc = g.admin.admin_read_model.get_staff_by_user_id(user_oid)
    if not staff_doc:
        raise AppBaseException(
            message="No staff profile for current user",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.AUTHENTICATION,
            status_code=403,
            user_message="No staff profile found",
            recoverable=False,
        )

    return staff_doc["_id"]   # staff._id




# -----------------------------
# Get current student ID (student._id)
# -----------------------------
def get_current_student_id() -> ObjectId:
    # 1) IAM user ObjectId
    user_oid = get_current_user_oid()
    student_doc = g.admin.admin_read_model.admin_get_student_by_user_id(user_oid)
    if not student_doc:
        raise AppBaseException(
            message="No student profile for current user",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.AUTHENTICATION,
            status_code=403,
            user_message="No student profile found",
            recoverable=False,
        )

    return student_doc["_id"]
# -----------------------------
# Get full current user info (from JWT payload)
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
                recoverable=False,
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
            recoverable=False,
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
            recoverable=False,
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
            recoverable=False,
        )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        user_id = payload.get("id")    # IAM._id as string
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
            recoverable=False,
        )
    except jwt.InvalidTokenError as e:
        raise AppBaseException.from_exception(
            e,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.AUTHENTICATION,
            status_code=401,
            user_message="Invalid authentication credentials",
            recoverable=False,
        )