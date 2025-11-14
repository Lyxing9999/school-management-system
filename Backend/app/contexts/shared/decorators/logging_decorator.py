from functools import wraps
from time import time
from app.contexts.core.log.log_service import LogService
def log_operation(level="INFO"):
    """
    Decorator to log the start and end of a function automatically using LogService.
    Assumes the class has `_log_service` attribute or uses LogService singleton.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            log_service = getattr(self, "_log_service", None) or LogService.get_instance()
            user_id = kwargs.get("user_id") 
            extra = kwargs.get("extra", {})

            start_time = time()
            log_service.log(f"{func.__name__} - start", level=level, module=self.__class__.__name__, user_id=user_id, extra=extra)

            try:
                result = func(self, *args, **kwargs)
                return result
            finally:
                duration_ms = (time() - start_time) * 1000
                extra["duration_ms"] = duration_ms
                log_service.log(f"{func.__name__} - end", level=level, module=self.__class__.__name__, user_id=user_id, extra=extra)
        return wrapper
    return decorator