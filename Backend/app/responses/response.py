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
        data: Optional[Any] = None,
        code: str = "ERROR",
        meta: Optional[Dict[str, Any]] = None,
        details: Optional[Dict[str, Any]] = None,
        errors: Optional[Union[str, Dict[str, Any]]] = None,
        category: ErrorCategory = ErrorCategory.SYSTEM,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        status_code: int = 400,
        hint: Optional[str] = None,
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
            "hint": hint,
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
    ) -> FlaskResponse:
        if hasattr(error, "to_dict"):
            # Get dict representation
            error_dict = error.to_dict()
            data = None  # Don't put full error object into 'data'
            details = error_dict.get('details', {})
            error_code = error_dict.get('error', error_code)
            category = error_dict.get('category', category)
            severity = error_dict.get('severity', severity)
            status_code = error_dict.get('status_code', status_code)
            hint = error_dict.get('hint', hint)
            errors = errors or error_dict.get('error')
        if serialize_data:
            data = serialize_for_json(data)
        if serialize_details:
            details = serialize_for_json(details)
        meta = meta or {}
        if serialize_meta:
            meta = serialize_for_json(meta)
        if not details and data and isinstance(data, dict) and 'details' in data:
            details = data['details']
        if not hint:
            hint = Response.generate_hint(error_code, details or {})
        if error:
            message = getattr(error, "message", None) or message or "An error occurred"
        if category:
            category = category.value if isinstance(category, Enum) else category
        if severity: 
            severity = severity.value if isinstance(severity, Enum) else severity
        if hint:
            hint = hint.value if isinstance(hint, Enum) else hint
        return Response.error_response(
            message=message or "An error occurred",
            data=data,
            details=details,
            errors=errors,
            code=error_code,
            status_code=status_code,
            category=category.value if isinstance(category, Enum) else category,
            severity=severity.value if isinstance(severity, Enum) else severity,
            meta=meta,
            hint=hint,
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