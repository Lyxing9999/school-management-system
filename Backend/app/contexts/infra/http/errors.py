from werkzeug.exceptions import HTTPException
from app.contexts.infra.http.responses import Response
from app.contexts.core.error.app_base_exception import AppBaseException , handle_exception

def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        return Response.http_error_response(error=error), getattr(error, "status_code", 500)

    @app.errorhandler(AppBaseException)
    def handle_custom_validation(error: AppBaseException):
        error = handle_exception(error)
        return Response._prepare_error_response(error=error)

    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception):
        error = handle_exception(error)
        return Response._prepare_error_response(error=error), 500