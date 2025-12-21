from __future__ import annotations

from functools import wraps
from app.contexts.core.error.mongo_error_mixin import MongoErrorMixin
from app.contexts.core.log.log_service import LogService


def mongo_operation(operation_name: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            self_obj = args[0] if args else None
            module_name = self_obj.__class__.__name__ if self_obj is not None else func.__module__
            logger = (
                getattr(self_obj, "_log_service", None)
                or getattr(self_obj, "logger", None)
                or LogService.get_instance()
            )

            try:
                result = func(*args, **kwargs)
                logger.log(
                    f"Mongo operation '{operation_name}' succeeded",
                    level="INFO",
                    module=module_name,
                    extra={"operation": operation_name, "success": True},
                )
                return result

            except Exception as e:
                logger.log(
                    f"Mongo operation '{operation_name}' failed",
                    level="ERROR",
                    module=module_name,
                    extra={
                        "operation": operation_name,
                        "error_type": type(e).__name__,
                        "error": str(e),
                        "success": False,
                    },
                )

                if isinstance(self_obj, MongoErrorMixin):
                    handled = self_obj._handle_mongo_error(operation_name, e)


                    if isinstance(handled, Exception):
                        raise handled

                    raise

                raise

        return wrapper
    return decorator