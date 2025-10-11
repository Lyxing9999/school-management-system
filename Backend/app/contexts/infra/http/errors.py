from flask import request
import traceback
from werkzeug.exceptions import HTTPException
from app.contexts.infra.http.responses import Response
from app.contexts.core.error.app_base_exception import AppBaseException, handle_exception
from app.contexts.core.log.log_service import LogService

log_service = LogService.get_instance()

def register_error_handlers(app):
    def get_error_context():
        return {
            "path": request.path,
            "method": request.method,
            "args": request.args.to_dict(),
            "json": request.get_json(silent=True),
            "form": request.form.to_dict(),
            "headers": dict(request.headers)
        }

    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        context = get_error_context()
        context["status_code"] = getattr(error, "code", 500)
        context["stack"] = traceback.format_exc()
        log_service.log(f"HTTPException: {str(error)}", level="ERROR", module="FlaskErrorHandler", extra=context)
        return Response.http_error_response(error=error), getattr(error, "code", 500)

    @app.errorhandler(AppBaseException)
    def handle_custom_validation(error: AppBaseException):
        context = get_error_context()
        context["type"] = type(error).__name__
        context["stack"] = traceback.format_exc()
        log_service.log(f"AppBaseException: {str(error)}", level="ERROR", module="FlaskErrorHandler", extra=context)
        error = handle_exception(error)
        return Response._prepare_error_response(error=error)

    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception):
        context = get_error_context()
        context["type"] = type(error).__name__
        context["stack"] = traceback.format_exc()
        log_service.log(f"Unexpected Exception: {str(error)}", level="CRITICAL", module="FlaskErrorHandler", extra=context)
        error = handle_exception(error)
        # Pass received_value or payload to response if needed
        return Response._prepare_error_response(
            error=error,
            data=context["json"] or context["form"] or None,
            details={"request_info": context}
        ), 500