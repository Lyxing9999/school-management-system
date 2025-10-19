from functools import wraps
from time import time
import traceback
from flask import request
from pydantic import BaseModel, RootModel
from app.contexts.infra.http.responses import Response
from app.contexts.core.log.log_service import LogService
from app.contexts.core.error.app_base_exception import AppBaseException, handle_exception
from app.contexts.common.base_response_dto import BaseResponseDTO

log_service = LogService.get_instance()


def wrap_response(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time()
        try:
            result = func(*args, **kwargs)

            # Default message
            default_message = f"{func.__name__.replace('_', ' ').title()} executed successfully"

            # BaseResponseDTO
            if isinstance(result, BaseResponseDTO):
                data = result.data
                if isinstance(data, BaseModel):
                    if isinstance(data, RootModel):
                        data = [x.model_dump(mode="json", exclude_none=True) for x in data.__root__]
                    else:
                        data = data.model_dump(mode="json", exclude_none=True)
                elif isinstance(data, list) and all(isinstance(x, BaseModel) for x in data):
                    data = [x.model_dump(mode="json", exclude_none=True) for x in data]
                return Response.success_response(
                    data=data,
                    message=getattr(result, "message", default_message),
                    success=getattr(result, "success", True)
                )

            # Plain BaseModel
            elif isinstance(result, BaseModel):
                return Response.success_response(
                    data=result.model_dump(mode="json", exclude_none=True),
                    message=default_message,
                    success=True
                )

            # Plain dict/list
            elif isinstance(result, (dict, list)):
                return Response.success_response(
                    data=result,
                    message=default_message,
                    success=True
                )

            # fallback for any other type
            return Response.success_response(
                data={"result": result},
                message=default_message,
                success=True
            )

        except AppBaseException as e:
            log_service.log(
                f"AppBaseException: {str(e)}",
                level="ERROR",
                module=func.__module__,
                extra={
                    "path": request.path,
                    "method": request.method,
                    "args": request.args.to_dict(),
                    "json": request.get_json(silent=True),
                    "form": request.form.to_dict(),
                    "headers": dict(request.headers),
                    "stack": traceback.format_exc(),
                }
            )
            return Response._prepare_error_response(error=e)

        except Exception as e:
            log_service.log(
                f"Unexpected Exception: {str(e)}",
                level="CRITICAL",
                module=func.__module__,
                extra={
                    "path": request.path,
                    "method": request.method,
                    "args": request.args.to_dict(),
                    "json": request.get_json(silent=True),
                    "form": request.form.to_dict(),
                    "headers": dict(request.headers),
                    "stack": traceback.format_exc(),
                }
            )
            app_exc = handle_exception(e)
            return Response._prepare_error_response(error=app_exc)

    return wrapper