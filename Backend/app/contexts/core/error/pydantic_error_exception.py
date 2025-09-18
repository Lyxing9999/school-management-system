# pydantic_error_exception.py
from typing import Any, Dict, Optional
from app.contexts.core.error.app_base_exception import AppBaseException, ErrorSeverity, ErrorCategory
import logging
logger = logging.getLogger(__name__)


class PydanticBaseValidationError(AppBaseException):
    def __init__(
        self,
        message: str,
        cause: Exception,
        details: Optional[Dict[str, Any]] = None,
        hint: Optional[str] = None,
        user_message: Optional[str] = None
    ):
        super().__init__(
            message=message,
            cause=cause,
            details=details or {},
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.VALIDATION,
            status_code=400,
            user_message=user_message,
            recoverable=True,
            hint=hint or "Check input data for correct types and required fields."
        )


class AppTypeError(AppBaseException):
    def __init__(
        self,
        message: str,
        cause: Exception,
        details: Optional[Dict[str, Any]] = None,
        hint: Optional[str] = None,
        user_message: Optional[str] = None
    ):
        super().__init__(
            message=message,
            cause=cause,
            details=details or {},
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.VALIDATION,
            status_code=400,
            user_message=user_message,
            recoverable=True,
            hint=hint or "Ensure all fields have the correct types."
        )

