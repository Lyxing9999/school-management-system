from werkzeug.exceptions import HTTPException
from app.responses.response import Response
from app.error.exceptions import (
    AppBaseException,
    AppTypeError,
    UnauthorizedError,
    PydanticBaseValidationError,
    ForbiddenError,
    NotFoundError,
    BadRequestError,
    InternalServerError,
    AuthenticationError,
    DatabaseError,
    NetworkError,
    AppDuplicateKeyError,
)

def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        return Response.http_error_response(error), getattr(error, "status_code", 500)

    @app.errorhandler(PydanticBaseValidationError)
    def handle_custom_validation(error: PydanticBaseValidationError):
        return Response.validation_error_response(error), getattr(error, "status_code", 400)

    @app.errorhandler(BadRequestError)
    def handle_bad_request(error: BadRequestError):
        return Response.bad_request_response(error), getattr(error, "status_code", 400)

    @app.errorhandler(NotFoundError)
    def handle_not_found(error: NotFoundError):
        return Response.not_found_response(error), getattr(error, "status_code", 404)

    @app.errorhandler(DatabaseError)
    def handle_database_error(error: DatabaseError):
        return Response.database_error_response(error), getattr(error, "status_code", 500)
    
    @app.errorhandler(AuthenticationError)
    def handle_authentication_error(error: AuthenticationError):
        return Response.authentication_error_response(error), getattr(error, "status_code", 401)
    @app.errorhandler(UnauthorizedError)
    def handle_unauthorized(error: UnauthorizedError):
        return Response.unauthorized_response(error), getattr(error, "status_code", 401)

    @app.errorhandler(ForbiddenError)
    def handle_forbidden(error: ForbiddenError):
        return Response.forbidden_response(error), getattr(error, "status_code", 403)

    @app.errorhandler(AppTypeError)
    def handle_app_type_error(error: AppTypeError):
        return Response.app_type_error_response(error), getattr(error, "status_code", 400)

    @app.errorhandler(AppBaseException)
    def handle_app_base_exception(error: AppBaseException):
        return Response.error_response(error), getattr(error, "status_code", 400)

    @app.errorhandler(InternalServerError)
    def handle_internal_server_error(error: InternalServerError):
        return Response.internal_server_error_response(error), getattr(error, "status_code", 500)
    
    @app.errorhandler(NetworkError)
    def handle_network_error(error: NetworkError):
        return Response.network_error_response(error), getattr(error, "status_code", 500)

    @app.errorhandler(AppDuplicateKeyError)
    def handle_app_duplicate_key_error(error: AppDuplicateKeyError):
        return Response.duplicate_key_error_response(error), getattr(error, "status_code", 400)