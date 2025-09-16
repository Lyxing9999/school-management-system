from functools import wraps
from app.contexts.common.base_response_dto import BaseResponseDTO
from app.contexts.infra.http.responses import Response
from app.contexts.core.error.app_base_exception import AppBaseException, handle_exception


from pydantic import BaseModel, RootModel

def wrap_response(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)

            if isinstance(result, BaseResponseDTO):
                data = result.data

                # If it's a Pydantic BaseModel
                if isinstance(data, BaseModel):
                    # special handling for RootModel
                    if isinstance(data, RootModel):
                        data = [x.model_dump(mode="json", exclude_none=True) for x in data.__root__]
                    else:
                        data = data.model_dump(mode="json", exclude_none=True)

                # If it's a list of BaseModels
                elif isinstance(data, list) and all(isinstance(x, BaseModel) for x in data):
                    data = [x.model_dump(mode="json", exclude_none=True) for x in data]

                return Response.success_response(
                    data=data,
                    message=result.message,
                    success=result.success
                )
            return result

        except AppBaseException as e:
            return Response._prepare_error_response(error=e)
        except Exception as e:
            app_exc = handle_exception(e)
            return Response._prepare_error_response(error=app_exc)

    return wrapper