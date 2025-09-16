
from typing import Optional, Dict, Any
from enum import Enum
import logging
import json
logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """Severity levels for exceptions."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """Categories for different types of errors."""
    VALIDATION = "validation"
    INFO = "info"
    WARNING = "warning"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATABASE = "database"
    NETWORK = "network"
    BUSINESS_LOGIC = "business_logic"
    SYSTEM = "system"

class AppBaseException(Exception):
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 400,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.SYSTEM,
        cause: Optional[Exception] = None,
        user_message: Optional[str] = None,
        recoverable: bool = True,
        hint: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        received_value: Optional[Any] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self._generate_error_code()
        self.details = details or {}
        self.severity = severity
        self.category = category
        self.cause = cause
        self.status_code = status_code
        self.recoverable = recoverable
        self.context = context or {}
        self.user_message = user_message or self._generate_user_message()
        self.hint = hint
        self.received_value = received_value
        # Log the exception based on severity
        self._log_exception()
    
    def _generate_error_code(self) -> str:
        """Generate a default error code based on the exception class."""
        return f"{self.__class__.__name__.upper()}_ERROR"
    
    def _generate_user_message(self) -> str:
        """Generate a user-friendly message."""
        return "An error occurred. Please try again or contact support."
    
    def _log_exception(self):
        """Log the exception with appropriate level based on severity."""
        log_data = { 'error_code': self.error_code, 'error_message': self.message,  'category': self.category.value,'severity': self.severity.value,'recoverable': self.recoverable,'details': self.details,'context': self.context}
        
        if self.severity == ErrorSeverity.CRITICAL:
            logger.critical(f"Critical error: {self.message}", extra=log_data)
        elif self.severity == ErrorSeverity.HIGH:
            logger.error(f"High severity error: {self.message}", extra=log_data)
        elif self.severity == ErrorSeverity.MEDIUM:
            logger.warning(f"Medium severity error: {self.message}", extra=log_data)
        else:
            logger.info(f"Low severity error: {self.message}", extra=log_data)
    


    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        return {
            'error': self.error_code,
            'status_code': self.status_code,
            'message': self.message,
            'user_message': self.user_message,
            'details': self.details,
            'severity': self.severity.value if hasattr(self.severity, 'value') else self.severity,
            'category': self.category.value if hasattr(self.category, 'value') else self.category,
            'recoverable': self.recoverable,
            'context': self.context,
            'hint': self.hint,
            'received_value': self.received_value,
        }

    def add_context(self, key: str, value: Any) -> 'AppBaseException':
        """Add context information to the exception."""
        self.context[key] = value
        return self
    
    def with_details(self, **kwargs) -> 'AppBaseException':
        """Add multiple details to the exception."""
        self.details.update(kwargs)
        return self

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


    @classmethod
    def from_exception(cls, exc: Exception, **kwargs) -> 'AppBaseException':
        return cls(
            message=str(exc),
            cause=exc,
            **kwargs
        )
    def __str__(self) -> str:
        return f"{self.error_code}: {self.message}"
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.error_code}: {self.message})"
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, AppBaseException):
            return False
        return self.error_code == other.error_code and self.message == other.message

def handle_exception(e: Exception) -> AppBaseException:
    if isinstance(e, AppBaseException):
        return e
    return AppBaseException.from_exception(e)
    