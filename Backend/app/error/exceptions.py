from pydantic import ValidationError as PydanticValidationError
from typing import Optional, Dict, Any, Union
from enum import Enum
import logging
import json

from pymongo.errors import DuplicateKeyError
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
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATABASE = "database"
    NETWORK = "network"
    BUSINESS_LOGIC = "business_logic"
    SYSTEM = "system"

class AppBaseException(Exception):
    """
    Base exception for custom app-level errors.
    
    Provides rich error context, logging, and standardized error handling.
    """
    
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
        context: Optional[Dict[str, Any]] = None
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
            'details': self.details,
            'severity': self.severity.value if hasattr(self.severity, 'value') else self.severity,
            'category': self.category.value if hasattr(self.category, 'value') else self.category,
            'recoverable': self.recoverable,
            'context': getattr(self.context, 'name', self.context.__class__.__name__ if self.context else 'unknown'),
            'hint': self.hint,
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


class NotFoundError(AppBaseException):
    """Raised when a requested resource is not found."""
    
    def __init__(
        self,
        message: str = "Resource not found",
        severity: ErrorSeverity = ErrorSeverity.LOW,
        category: ErrorCategory = ErrorCategory.BUSINESS_LOGIC,
        resource_type: Optional[str] = None,
        status_code: int = 404,
        cause: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None,
        resource_id: Optional[Union[str, int]] = None,
        user_message: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.pop('details', {})
            
        super().__init__(
            message=message,
            details=details,
            severity=severity,
            category=category,
            status_code=status_code,
            cause=cause,
            context=context,
            user_message=user_message,
            **kwargs
        )


class PydanticBaseValidationError(AppBaseException):
    """Raised when data validation fails."""
    
    def __init__(
        self,
        message: str = "Validation failed",
        field_errors: Optional[Dict[str, str]] = None,
        cause: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None,
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None,
        hint: Optional[str] = None,
        **kwargs
    ):
    
        details = details or {}
        details.update(kwargs.pop('details', {}))
        if field_errors:
            details['field_errors'] = field_errors
            
        super().__init__(
            message=message,
            details=details,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.VALIDATION,
            status_code=status_code or 400,
            cause=cause,
            context=context,
            user_message=user_message,
            hint=hint,
            **kwargs
        )


class DatabaseError(AppBaseException):
    """Raised when database operations fail."""
    
    def __init__(
        self,
        severity: ErrorSeverity = ErrorSeverity.HIGH,
        category: ErrorCategory = ErrorCategory.DATABASE,
        cause: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None,
        message: str = "Database operation failed",
        operation: Optional[str] = None,
        table: Optional[str] = None,
        status_code: Optional[int] = None,
        user_message: Optional[str] = None,
        **kwargs
    ):
        details = details or {}
        details.update(kwargs.pop('details', {}))
        if operation:
            details['operation'] = operation
        if table and not details.get('table'):
            details['table'] = table
        if details:
            details.update(kwargs.pop('details', {}))
            
        super().__init__(
            message=message,
            details=details,
            severity=severity,
            category=category,
            cause=cause,
            context=context,
            recoverable=False,
            status_code=status_code or 500,
            user_message=user_message,
            **kwargs
        )


class AuthenticationError(AppBaseException):
    """Raised when authentication fails."""
    
    def __init__(
        self,
        message: str = "Authentication failed",
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.AUTHENTICATION,
        auth_method: Optional[str] = None,
        status_code: Optional[int] = None,
        cause: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None,
        recoverable: bool = False,
        user_message: Optional[str] = None,
        **kwargs
    ):
        details = details or {}
        details.update(kwargs.pop('details', {}))
        if auth_method and not details.get('auth_method'):
            details['auth_method'] = auth_method
            
        super().__init__(
            
            message=message,
            details=details,
            severity=severity,
            category=category,
            status_code=status_code or 401,
            cause=cause,
            context=context,
            recoverable=recoverable,
            user_message=user_message,
            **kwargs
        )


class BadRequestError(AppBaseException):
    """Raised when request is malformed or invalid."""
    
    def __init__(
        self,
        message: str = "Bad request",
        severity: ErrorSeverity = ErrorSeverity.LOW,
        category: ErrorCategory = ErrorCategory.VALIDATION,
        status_code: Optional[int] = None,
        user_message: Optional[str] = None,
        hint: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.pop('details', {})
        super().__init__(
            message=message,
            severity=severity,
            category=category,
            status_code=status_code or 400,
            details=details,
            user_message=user_message,
            hint=hint,
            **kwargs
        )


class InternalServerError(AppBaseException):
    """Raised when an unexpected internal error occurs."""
    
    def __init__(
        self,
        message: str = "Internal server error",
        severity: ErrorSeverity = ErrorSeverity.CRITICAL,
        category: ErrorCategory = ErrorCategory.SYSTEM,
        cause: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None,
        status_code: Optional[int] = None,
        user_message: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.pop('details', {})
        super().__init__(
            message=message,
            severity=severity,
            category=category,
            status_code=status_code or 500,
            recoverable=False,
            cause=cause,
            context=context,
            details=details,
            **kwargs
        )


class UnauthorizedError(AppBaseException):
    """Raised when user lacks valid authentication."""
    
    def __init__(
        self,
        message: str = "Unauthorized access",
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.AUTHENTICATION,
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None,
        **kwargs
    ):
        details = details or {}
        super().__init__(
            message=message,
            severity=severity,
            category=category,
            status_code=status_code or 401,
            user_message=user_message,
            **kwargs
        )


class ForbiddenError(AppBaseException):
    """Raised when user lacks necessary permissions."""
    
    def __init__(
        self,
        message: str = "Access forbidden",
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.AUTHORIZATION,
        required_permission: Optional[str] = None,
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.pop('details', {})
        if required_permission and not details.get('required_permission'):
            details['required_permission'] = required_permission
            
        super().__init__(
            message=message,
            details=details,
            severity=severity,
            category=category,
            status_code=status_code or 403,
            cause=cause,
            context=context,
            user_message=user_message,
            **kwargs
        )


class NetworkError(AppBaseException):
    """Raised when network operations fail."""
    
    def __init__(
        self,
        message: str = "Network error",
        endpoint: Optional[str] = None,
        severity: ErrorSeverity = ErrorSeverity.HIGH,
        category: ErrorCategory = ErrorCategory.NETWORK,
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.pop('details', {})
        if endpoint and not details.get('endpoint'):
            details['endpoint'] = endpoint
        if status_code:
            details['status_code'] = status_code
            
        super().__init__(
            message=message,
            details=details,
            severity=severity,
            category=category,
            status_code=status_code or 500,
            cause=cause,
            context=context,
            user_message=user_message,
            **kwargs
        )

class AppTypeError(AppBaseException):
    def __init__(
        self,
        message: str = "Type error",
        type_name: Optional[str] = None,
        severity: ErrorSeverity = ErrorSeverity.LOW,
        category: ErrorCategory = ErrorCategory.VALIDATION,
        status_code: Optional[int] = None,
        cause: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None,
        details: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.pop('details', {})
        if type_name and not details.get('type_name'):
            details['type_name'] = type_name
        super().__init__(
            message=message,
            details=details,
            severity=severity,
            category=category,
            status_code=status_code or 400,
            user_message=user_message,
            cause=cause,
            context=context,
            **kwargs
        )

class ConfigurationError(AppBaseException):
    """Raised when configuration is invalid or missing."""
    
    def __init__(
        self,
        message: str = "Configuration error",
        config_key: Optional[str] = None,
        severity: ErrorSeverity = ErrorSeverity.CRITICAL,
        category: ErrorCategory = ErrorCategory.SYSTEM,
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None,
        cause: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        details = kwargs.pop('details', {})
        if config_key and not details.get('config_key'):
            details['config_key'] = config_key
            
        super().__init__(
            message=message,
            details=details,
            severity=severity,
            category=category,
            recoverable=False,
            status_code=status_code or 500,
            user_message=user_message,
            cause=cause,
            context=context,
            **kwargs
        )


class BusinessLogicError(AppBaseException):
    """Raised when business rules are violated."""
    
    def __init__(
        self,
        message: str = "Business rule violation",
        rule: Optional[str] = None,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.BUSINESS_LOGIC,
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None,
        cause: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        details = kwargs.pop('details', {})
        if rule and not details.get('violated_rule'):
            details['violated_rule'] = rule
            
        super().__init__(
            message=message,
            details=details,
            severity=severity,
            category=category,
            status_code=status_code or 400,
            **kwargs
        )

class AppDuplicateKeyError(AppBaseException):
    def __init__(self,
     message: str = "Duplicate key error",
     key: Optional[str] = None,
     details: Optional[Dict[str, Any]] = None,
     status_code: Optional[int] = None,
     context: Optional[Dict[str, Any]] = None,
     severity: ErrorSeverity = ErrorSeverity.LOW,
     category: ErrorCategory = ErrorCategory.DATABASE,
     user_message: Optional[str] = None,
     **kwargs):
        details = kwargs.pop('details', {})
        if key and not details.get('key'):
            details['key'] = key
        super().__init__(
            message=message,
            details=details,
            status_code=status_code or 400,
            severity=severity,
            category=category,
            context=context,
            user_message=user_message,
            **kwargs)


class RateLimitError(AppBaseException):
    """Raised when rate limits are exceeded."""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        limit: Optional[int] = None,
        reset_time: Optional[int] = None,
        severity: ErrorSeverity = ErrorSeverity.LOW,
        category: ErrorCategory = ErrorCategory.BUSINESS_LOGIC,
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.pop('details', {})
        if limit:
            details['limit'] = limit
        if reset_time:
            details['reset_time'] = reset_time
            
        super().__init__(
            message=message,
            details=details,
            severity=severity,
            category=category,
            status_code=status_code or 400,
            user_message=user_message,
            **kwargs
        )


class ExceptionFactory:
    """Factory to create common app exceptions."""

    @staticmethod
    def not_found(resource_type: str, resource_id: Union[str, int]) -> NotFoundError:
        return NotFoundError(
            message=f"{resource_type} with ID {resource_id} not found",
            resource_type=resource_type,
            resource_id=resource_id,
            status_code=404,
            cause=None,
        )
    

    @staticmethod
    def database_connection_failed(database: str, context: Optional[Dict[str, Any]] = None, details: Optional[Dict[str, Any]] = None) -> DatabaseError:
        return DatabaseError(
            message=f"Failed to connect to database: {database}",
            operation="connect",
            status_code=500,
            cause=None,
            context=context,
        )

    @staticmethod
    def unauthorized_access(resource: str, context: Optional[Dict[str, Any]] = None) -> UnauthorizedError:
        return UnauthorizedError(
            message=f"Unauthorized access to {resource}",
            details={"resource": resource},
            status_code=401,
            cause=None,
            context=context,
        )

    @staticmethod
    def app_type_error(
        type_name: str,
        received_value: Any,
        context: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None,
        **kwargs
    ) -> AppTypeError:
        return AppTypeError(
            message=f"Expected '{type_name}', got '{type(received_value).__name__}'",
            details={"expected_type": type_name, "received_value": received_value},
            user_message=user_message,
            context=context,
            status_code=400,
            cause=None,
            **kwargs
        )

    @staticmethod
    def validation_failed(field: str, value: Any, reason: str, context: Optional[Dict[str, Any]] = None, user_message: Optional[str] = None, **kwargs) -> PydanticBaseValidationError:
        return PydanticBaseValidationError(
            message=f"Validation failed for '{field}': {reason}",
            field_errors={field: reason},
            status_code=400,
            cause=None,
            value=value,
            context=context,
            user_message=user_message,
            **kwargs
        )


def handle_exception(
    exc: Exception,
    context: Optional[Dict[str, Any]] = None,
    user_message: Optional[str] = None
) -> AppBaseException:
    context = context or {}
    if isinstance(exc, AppBaseException):
        if context:
            for key, value in context.items():
                exc.add_context(key, value)
        if user_message:
            exc.user_message = user_message
        return exc
    exception_mapping = {
        PydanticBaseValidationError: PydanticBaseValidationError,
        NotFoundError: NotFoundError,
        AppTypeError: AppTypeError,
        DuplicateKeyError: AppDuplicateKeyError,
        BadRequestError: BadRequestError,
        UnauthorizedError: UnauthorizedError,
        ForbiddenError: ForbiddenError,
        DatabaseError: DatabaseError,
        AuthenticationError: AuthenticationError,
        TypeError: AppTypeError,  
        ValueError: PydanticBaseValidationError,  
        KeyError: NotFoundError,
        ConnectionError: NetworkError
    }

    for exc_type, app_exc_cls in exception_mapping.items():
        if isinstance(exc, exc_type):
            return app_exc_cls(
                message=str(exc),
                cause=exc,
                context=context,
                user_message=user_message
            )

    return InternalServerError(
        message=f"Unexpected error: {str(exc)}",
        cause=exc,
        context=context,
        user_message=user_message or "An unexpected error occurred."
    )