from app.contexts.core.error.app_base_exception import (
    AppBaseException,
    ErrorCategory,
    ErrorSeverity,
)
from typing import Any, Dict


class EnrollmentException(AppBaseException):
    """Base exception for all enrollment-related errors."""

    def __init__(
        self,
        message: str,
        error_code: str = "ENROLLMENT_ERROR",
        status_code: int = 400,
        details: Dict[str, Any] | None = None,
        **kwargs,
    ):
        severity = kwargs.pop("severity", ErrorSeverity.MEDIUM)

        super().__init__(
            message=message,
            error_code=error_code,
            category=ErrorCategory.BUSINESS_LOGIC,
            severity=severity,
            status_code=status_code,
            details=details,
            **kwargs,
        )


class InvalidEnrollmentStatusException(EnrollmentException):
    """Raised when an invalid status value is passed."""

    def __init__(self, received_value: Any):
        super().__init__(
            message=f"Invalid enrollment status: {received_value}",
            error_code="INVALID_ENROLLMENT_STATUS",
            status_code=422,
            severity=ErrorSeverity.HIGH,
            details={"received": received_value},
            hint="Allowed values: active, dropped, completed",
            received_value=received_value,
        )


class EnrollmentAlreadyCompletedException(EnrollmentException):
    """Cannot modify a completed enrollment."""

    def __init__(self, enrollment_id: Any):
        super().__init__(
            message="Enrollment is already completed.",
            error_code="ENROLLMENT_ALREADY_COMPLETED",
            status_code=409,
            severity=ErrorSeverity.HIGH,
            details={"enrollment_id": str(enrollment_id)},
            hint="Completed enrollment records are immutable.",
        )


class EnrollmentAlreadyDroppedException(EnrollmentException):
    """Cannot drop an already dropped enrollment."""

    def __init__(self, enrollment_id: Any):
        super().__init__(
            message="Enrollment has already been dropped.",
            error_code="ENROLLMENT_ALREADY_DROPPED",
            status_code=409,
            severity=ErrorSeverity.MEDIUM,
            details={"enrollment_id": str(enrollment_id)},
            hint="Drop status cannot be applied twice.",
        )