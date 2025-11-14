from functools import wraps
from app.contexts.core.error.mongo_error_mixin import MongoErrorMixin
from app.contexts.core.log.log_service import LogService

def mongo_operation(operation_name: str):
    """
    Decorator to handle MongoDB operation logging and error handling.
    Automatically logs success or failure using LogService.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            self = args[0] if args else None
            mixin = self if isinstance(self, MongoErrorMixin) else MongoErrorMixin()
            logger = getattr(self, "logger", LogService.get_instance())

            try:
                result = func(*args, **kwargs)
                logger.log(
                    f"Mongo operation '{operation_name}' succeeded",
                    level="INFO",
                    module=self.__class__.__name__,
                    extra={"operation": operation_name, "success": True}
                )
                return result
            except Exception as e:
                logger.log(
                    f"Mongo operation '{operation_name}' failed",
                    level="ERROR",
                    module=self.__class__.__name__,
                    extra={
                        "operation": operation_name,
                        "error": str(e),
                        "success": False
                    }
                )
                raise mixin._handle_mongo_error(operation_name, e)
        return wrapper
    return decorator