from app.contexts.core.errors.app_base_exception import (
    AppBaseException,
    ErrorCategory,
    ErrorSeverity,
)
from typing import Any, Dict


class InvalidEnrollmentStatusException(AppBaseException):
    """Raised when an invalid status value is passed."""

    def __init__(self, received_value: Any):
        super().__init__(
            message=f"Invalid enrollment status: {received_value}",
            error_code="INVALID_ENROLLMENT_STATUS",
            status_code=422,
            severity=ErrorSeverity.HIGH,
            user_message="Invalid enrollment status provided.",
            details={"received": received_value},
            hint="Allowed values: active, dropped, completed",
            received_value=received_value,
        )


class EnrollmentAlreadyCompletedException(AppBaseException):
    """Cannot modify a completed enrollment."""

    def __init__(self, enrollment_id: Any):
        super().__init__(
            message="Enrollment is already completed.",
            error_code="ENROLLMENT_ALREADY_COMPLETED",
            status_code=409,
            severity=ErrorSeverity.HIGH,
            user_message="This enrollment has already been completed.",
            details={"enrollment_id": str(enrollment_id)},
            hint="Completed enrollment records are immutable.",
        )


class EnrollmentAlreadyDroppedException(AppBaseException):
    """Cannot drop an already dropped enrollment."""

    def __init__(self, enrollment_id: Any):
        super().__init__(
            message="Enrollment has already been dropped.",
            error_code="ENROLLMENT_ALREADY_DROPPED",
            status_code=409,
            severity=ErrorSeverity.MEDIUM,
            user_message="This enrollment has already been dropped.",
            details={"enrollment_id": str(enrollment_id)},
            hint="Drop status cannot be applied twice.",
        )