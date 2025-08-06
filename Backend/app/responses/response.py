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
    def generate_hint_from_field_errors(field_errors: Dict[str, Any]) -> str:
        if not field_errors:
            return ""
        return " | ".join(
            f"Check field '{field}': {msg}" for field, msg in field_errors.items()
        )
    @staticmethod
    def generate_hint(error_type: str, details: dict) -> str:
        if error_type == "VALIDATION_ERROR" and 'field_errors' in details:
            return Response.generate_hint_from_field_errors(details['field_errors'])
        elif error_type == "DUPLICATE_KEY_ERROR":
            return "Duplicate entry found. Ensure unique fields are not duplicated."
        elif error_type == "AUTHENTICATION_ERROR":
            return "Ensure you have provided correct credentials or valid token."
        return ""
    @staticmethod
    def error_response(
        message: str = "An error occurred",
        user_message: Optional[str] = None,
        data: Optional[Any] = None,
        code: str = "ERROR",
        meta: Optional[Dict[str, Any]] = None,
        details: Optional[Dict[str, Any]] = None,
        errors: Optional[Union[str, Dict[str, Any]]] = None,
        category: ErrorCategory = ErrorCategory.SYSTEM,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        status_code: int = 400,
        hint: Optional[str] = None,
        success: bool = False,
        received_value: Optional[Any] = None,
        recoverable: bool = True,
    ) -> FlaskResponse:
        response = {
            "success": success,
            "message": message,
            "user_message": user_message,
            "data": data,
            "details": details,
            "code": code,
            "meta": meta,
            "error": errors,
            "category": category.value if isinstance(category, Enum) else category,
            "severity": severity.value if isinstance(severity, Enum) else severity,
            "hint": hint,
            "recoverable": recoverable,
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
        hint: Optional[str] = None,
        success: bool = False,
        user_message: Optional[str] = None,
        recoverable: bool = True,
        received_value: Optional[Any] = None,
    ) -> FlaskResponse:

        if hasattr(error, "to_dict"):
            error_dict = error.to_dict()
            data = None  # Don't put full error object into 'data'
            details = error_dict.get('details', {})
            error_code = error_dict.get('error', error_code)
            category = error_dict.get('category', category)
            severity = error_dict.get('severity', severity)
            status_code = error_dict.get('status_code', status_code)
            hint = error_dict.get('hint', hint)
            errors = errors or error_dict.get('error')
            message = error_dict.get('message', message) or "An error occurred"
            user_message = error_dict.get('user_message', user_message)
            received_value = error_dict.get('received_value', received_value)
        # Serialize objects if required
        if serialize_data:
            data = serialize_for_json(data)
        if serialize_details:
            details = serialize_for_json(details)
        meta = meta or {}
        if serialize_meta:
            meta = serialize_for_json(meta)

        # Extract details from data if needed
        if not details and data and isinstance(data, dict) and 'details' in data:
            details = data['details']

        # Auto-generate hint if missing
        if not hint:
            hint = Response.generate_hint(error_code, details or {})

        # Fallback message if still None
        if error and not message:
            message = str(error) or "An error occurred"

        # Ensure user_message is always filled
        user_message = user_message or message or "An error occurred"
        received_value = received_value or details.get('received_value')
        # Convert Enums to their values
        category = category.value if isinstance(category, Enum) else category
        severity = severity.value if isinstance(severity, Enum) else severity
        hint = hint.value if isinstance(hint, Enum) else hint

        return Response.error_response(
            message=message,
            user_message=user_message,
            data=data,
            details=details,
            errors=errors,
            code=error_code,
            status_code=status_code,
            category=category,
            severity=severity,
            meta=meta,
            hint=hint,
            success=success,
            received_value=received_value,
            recoverable=recoverable,
        )

    @staticmethod
    def http_error_response(error: HTTPException) -> FlaskResponse:
        return Response.error_response(
            message=error.description or "HTTP error occurred",
            status_code=error.code or 500,
            hint=error.description or "An HTTP error happened",
            code=error.name.replace(" ", "_").upper() if hasattr(error, "name") else "HTTP_ERROR",
            category="http",
            severity="medium",
        )