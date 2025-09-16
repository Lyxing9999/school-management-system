
from pymongo.errors import DuplicateKeyError, PyMongoError
from bson.errors import InvalidId
from pydantic import ValidationError
from app.contexts.core.error.app_base_exception import AppBaseException , ErrorSeverity , ErrorCategory
from typing import Dict, Any

class DatabaseError(AppBaseException):
    """Represents errors related to database operations."""


class ValidationAppError(AppBaseException):
    """Represents Pydantic or input validation errors."""


class InternalServerError(AppBaseException):
    """Represents unexpected system errors."""


def make_details(operation: str, collection: str, details: str) -> Dict[str, Any]:
    """Utility to create a structured error details dict."""
    return {
        "operation": operation,
        "collection": collection,
        "details": details,
    }
class MongoErrorMixin:
    """Reusable error handler for MongoDB-related operations."""

    def _handle_mongo_error(self, operation: str, error: Exception, details: str = ""):
        if hasattr(self, "config") and hasattr(self.config, "collection"):
            collection = self.config.collection
        elif hasattr(self, "collection"):
            collection = getattr(self.collection, "name", "unknown_collection")
        else:
            collection = "unknown_collection"

        base_message = f"Failed to {operation} on collection '{collection}'"
        error_details = make_details(operation, collection, details)

        from pymongo.errors import DuplicateKeyError, PyMongoError
        from bson.errors import InvalidId
        from pydantic import ValidationError

        if isinstance(error, DuplicateKeyError):
            raise DatabaseError(
                message=f"{base_message}: Duplicate key error",
                cause=error,
                details=error_details,
                hint="Ensure unique index constraints are not violated.",
                severity=ErrorSeverity.MEDIUM,
                category=ErrorCategory.DATABASE,
                status_code=409,
                user_message="This record already exists.",
                recoverable=False,
            )

        if isinstance(error, InvalidId):
            raise DatabaseError(
                message=f"{base_message}: Invalid ObjectId format",
                cause=error,
                details=error_details,
                hint="Provide a valid MongoDB ObjectId string.",
                severity=ErrorSeverity.LOW,
                category=ErrorCategory.DATABASE,
                status_code=400,
                user_message="Invalid ID format provided.",
                recoverable=True,
            )

        if isinstance(error, PyMongoError):
            raise DatabaseError(
                message=f"{base_message}: {error}",
                cause=error,
                details=error_details,
                hint="Check database connection and query syntax.",
                severity=ErrorSeverity.HIGH,
                category=ErrorCategory.DATABASE,
                status_code=500,
                user_message="Database error occurred. Please try again later.",
                recoverable=False,
            )

        if isinstance(error, ValidationError):
            raise ValidationAppError(
                message=f"{base_message}: Validation failed",
                cause=error,
                details=error_details,
                hint="Ensure input data matches schema requirements.",
                severity=ErrorSeverity.LOW,
                category=ErrorCategory.VALIDATION,
                status_code=400,
                user_message="Invalid data format provided.",
                recoverable=True,
            )

        raise InternalServerError(
            message=f"{base_message}: {error}",
            cause=error,
            details=error_details,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.DATABASE,
            status_code=500,
            user_message="Unexpected server error occurred.",
            recoverable=False,
        )