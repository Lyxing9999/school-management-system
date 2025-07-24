from flask import jsonify
from typing import Optional, Union, Dict, Any
from flask.wrappers import Response as FlaskResponse
from app.error.exceptions import BadRequestError, ForbiddenError, InternalServerError, NotFoundError, PydanticBaseValidationError, UnauthorizedError, DatabaseError ,NetworkError ,AuthenticationError, ErrorCategory , ErrorSeverity, AppTypeError, AppDuplicateKeyError
from enum import Enum
from werkzeug.exceptions import HTTPException

def serialize_for_json(obj):
    import json
    return json.loads(json.dumps(obj, default=str))


class Response:

    @staticmethod
    def success_response(
        data: Optional[Any] = None,
        message: str = "",
        status_code: int = 200,
        metadata: Optional[Dict[str, Any]] = None
    ) -> FlaskResponse:
        response = {
            "success": True,
            "message": message,
            "data": data,
        }
        if metadata:
            response["metadata"] = metadata
        resp = jsonify(response)
        resp.status_code = status_code
        return resp

    @staticmethod
    def error_response(
        message: str = "An error occurred",
        data: Optional[Any] = None,
        code: str = "ERROR",
        meta: Optional[Dict[str, Any]] = None,
        details: Optional[Dict[str, Any]] = None,
        errors: Optional[Union[str, Dict[str, Any]]] = None,
        category: ErrorCategory = ErrorCategory.SYSTEM,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        status_code: int = 400,
    ) -> FlaskResponse:
        response = {
            "success": False,
            "message": message,
            "data": data,
            "details": details,
            "code": code,
            "meta": meta,
            "error": errors,
            "category": category.value if isinstance(category, Enum) else category,
            "severity": severity.value if isinstance(severity, Enum) else severity,
        }
        resp = jsonify(response)
        resp.status_code = status_code
        return resp

    @staticmethod
    def _prepare_error_response(
        *,
        error: Optional[Union[Exception, Dict[str, Any], str]] = None,
        message: Optional[str] = None,
        data: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None,
        errors: Optional[Union[str, Dict[str, Any]]] = None,
        status_code: int = 400,
        error_code: str = "ERROR",
        category: ErrorCategory = ErrorCategory.SYSTEM,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        meta: Optional[Dict[str, Any]] = None,
        serialize_details: bool = True,
        serialize_data: bool = True,
        serialize_meta: bool = True,
        extract_errors_from_error: bool = False,
    ) -> FlaskResponse:
        if error:
            message = getattr(error, "message", message) or message
            if hasattr(error, "to_dict"):
                data = error.to_dict()
                if 'details' in data and 'data' in data['details']:
                    data = data['details']['data']
            elif isinstance(error, dict):
                data = error
            elif isinstance(error, str):
                data = {"error": error}
            else:
                data = data or str(error)
            status_code = getattr(error, "status_code", status_code)
            if extract_errors_from_error:
                errors = getattr(error, "errors", errors)
        else:
            if data and serialize_data and hasattr(data, "model_dump"):
                data = data.model_dump()

        if serialize_data:
            data = serialize_for_json(data)
        if serialize_details:
            details = serialize_for_json(details)
        meta = meta or {}
        if serialize_meta:
            meta = serialize_for_json(meta)

        return Response.error_response(
            message=message or "An error occurred",
            data=data,
            details=details,
            errors=errors,
            code=error_code,
            status_code=status_code,
            category=category,
            severity=severity,
            meta=meta,
        )

    @staticmethod
    def validation_error_response(
        error: Optional[Union[PydanticBaseValidationError, Exception, Dict[str, Any], str]] = None,
        errors: Optional[Union[str, Dict[str, Any]]] = None,
        message: Optional[str] = None,
        status_code: int = 422,
        error_code: str = "VALIDATION_ERROR",
        data: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None,
        category: ErrorCategory = ErrorCategory.VALIDATION,
        severity: ErrorSeverity = ErrorSeverity.LOW,
    ) -> FlaskResponse:
        return Response._prepare_error_response(
            error=error,
            errors=errors,
            message=message or "Validation failed",
            status_code=status_code,
            error_code=error_code,
            data=data,
            details=details,
            extract_errors_from_error=True,
            category=category,
            severity=severity,
        )

    @staticmethod
    def not_found_response(
        error: Optional[Union[NotFoundError, Exception]] = None,
        message: str = "Resource not found",
        data: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None,
        error_code: str = "NOT_FOUND",
        status_code: int = 404,
        category: ErrorCategory = ErrorCategory.BUSINESS_LOGIC,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    ) -> FlaskResponse:
        return Response._prepare_error_response(
            error=error,
            message=message,
            data=data,
            details=details,
            status_code=status_code,
            error_code=error_code,
            category=category,
            severity=severity,
        )

    @staticmethod
    def unauthorized_response(
        error: Optional[Union[UnauthorizedError, Exception]] = None,
        message: str = "Unauthorized",
        data: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None,
        error_code: str = "UNAUTHORIZED",
        status_code: int = 401,
        category: ErrorCategory = ErrorCategory.AUTHENTICATION,
        severity: ErrorSeverity = ErrorSeverity.HIGH,
    ) -> FlaskResponse:
        return Response._prepare_error_response(
            error=error,
            message=message,
            data=data,
            details=details,
            status_code=status_code,
            error_code=error_code,
            category=category,
            severity=severity,
        )

    @staticmethod
    def forbidden_response(
        error: Optional[Union[ForbiddenError, Exception]] = None,
        message: str = "Forbidden",
        data: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None,
        error_code: str = "FORBIDDEN",
        status_code: int = 403,
        category: ErrorCategory = ErrorCategory.AUTHORIZATION,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    ) -> FlaskResponse:
        return Response._prepare_error_response(
            error=error,
            message=message,
            data=data,
            details=details,
            status_code=status_code,
            error_code=error_code,
            category=category,
            severity=severity,
        )

    @staticmethod
    def internal_server_error_response(
        error: Optional[Union[InternalServerError, Exception]] = None,
        message: str = "Internal server error",
        data: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None,
        error_code: str = "INTERNAL_SERVER_ERROR",
        status_code: int = 500,
        category: ErrorCategory = ErrorCategory.SYSTEM,
        severity: ErrorSeverity = ErrorSeverity.HIGH,
    ) -> FlaskResponse:
        return Response._prepare_error_response(
            error=error,
            message=message,
            data=data,
            details=details,
            status_code=status_code,
            error_code=error_code,
            category=category,
            severity=severity,
        )

    @staticmethod
    def bad_request_response(
        error: Optional[Union[BadRequestError, Exception]] = None,
        message: str = "Bad request",
        data: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None,
        error_code: str = "BAD_REQUEST",
        status_code: int = 400,
        category: ErrorCategory = ErrorCategory.VALIDATION,
        severity: ErrorSeverity = ErrorSeverity.LOW,
    ) -> FlaskResponse:
        return Response._prepare_error_response(
            error=error,
            message=message,
            data=data,
            details=details,
            status_code=status_code,
            error_code=error_code,
            category=category,
            severity=severity,
        )

    @staticmethod
    def network_error_response(
        error: Optional[Union[NetworkError, Exception]] = None,
        message: str = "Network error",
        data: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None,
        error_code: str = "NETWORK_ERROR",
        status_code: int = 500,
        meta: Optional[Dict[str, Any]] = None,
        category: ErrorCategory = ErrorCategory.NETWORK,
        severity: ErrorSeverity = ErrorSeverity.HIGH,
    ) -> FlaskResponse:
        return Response._prepare_error_response(
            error=error,
            message=message,
            data=data,
            details=details,
            status_code=status_code,
            error_code=error_code,
            meta=meta,
            category=category,
            severity=severity,
        )

    @staticmethod
    def database_error_response(
        error: Optional[Union[DatabaseError, Exception]] = None,
        message: str = "Database error",
        data: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None,
        error_code: str = "DATABASE_ERROR",
        status_code: int = 500,
        meta: Optional[Dict[str, Any]] = None,
        category: ErrorCategory = ErrorCategory.DATABASE,
        severity: ErrorSeverity = ErrorSeverity.HIGH,
    ) -> FlaskResponse:
        return Response._prepare_error_response(
            error=error,
            message=message,
            data=data,
            details=details,
            status_code=status_code,
            error_code=error_code,
            meta=meta,
            category=category,
            severity=severity,
        )
    @staticmethod
    def http_error_response(
        error: Optional[Union[HTTPException, Exception]] = None,
        message: str = "HTTP error",
        data: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None,
        error_code: str = "HTTP_ERROR",
        status_code: int = 500,
        meta: Optional[Dict[str, Any]] = None,
        category: ErrorCategory = ErrorCategory.SYSTEM,
        severity: ErrorSeverity = ErrorSeverity.HIGH,
    ) -> FlaskResponse:
        return Response._prepare_error_response(
            error=error,
            message=message,
            data=data,
            details=details,
            status_code=status_code,
            error_code=error_code,
            meta=meta,
            category=category,
            severity=severity,
        )

    @staticmethod
    def authentication_error_response(
        error: Optional[Union[AuthenticationError, Exception]] = None,
        message: str = "Authentication error",
        data: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None,
        error_code: str = "AUTHENTICATION_ERROR",
        status_code: int = 401,
        meta: Optional[Dict[str, Any]] = None,
        category: ErrorCategory = ErrorCategory.AUTHENTICATION,
        severity: ErrorSeverity = ErrorSeverity.HIGH,
    ) -> FlaskResponse:
        return Response._prepare_error_response(
            error=error,
            message=message,
            data=data,
            details=details,
            status_code=status_code,
            error_code=error_code,
            meta=meta,
            category=category,
            severity=severity,
        )

    @staticmethod
    def app_type_error_response(
        error: Optional[Union[AppTypeError, Exception]] = None,
        message: str = "Type error",
        data: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None,
        error_code: str = "TYPE_ERROR",
        status_code: int = 400,
        meta: Optional[Dict[str, Any]] = None,
    ) -> FlaskResponse:
        return Response._prepare_error_response(
            error=error,
            message=message,
            data=data,
            details=details,
            status_code=status_code,
            error_code=error_code,
            meta=meta,
        )

    @staticmethod
    def duplicate_key_error_response(
        error: Optional[Union[AppDuplicateKeyError, Exception]] = None,
        message: str = "Duplicate key error",
        data: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None,
        error_code: str = "DUPLICATE_KEY_ERROR",
        status_code: int = 400,
        meta: Optional[Dict[str, Any]] = None,
        category: ErrorCategory = ErrorCategory.DATABASE,
        severity: ErrorSeverity = ErrorSeverity.LOW,
    ) -> FlaskResponse:
        return Response._prepare_error_response(
            error=error,
            message=message,
            data=data,
            details=details,    
            status_code=status_code,
            error_code=error_code,
            meta=meta,
            category=category,
            severity=severity,
        )
    