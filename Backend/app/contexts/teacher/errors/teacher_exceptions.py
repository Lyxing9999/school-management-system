from app.contexts.core.errors import AppBaseException, ErrorSeverity, ErrorCategory
from bson import ObjectId


class TeacherForbiddenException(AppBaseException):
    def __init__(self):
        super().__init__(
            message="Teacher is not allowed to perform this action.",
            error_code="TEACHER_FORBIDDEN",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="You are not allowed to perform this action.",
            recoverable=False,
            hint="Contact the system administrator if you believe this is a mistake."
        )