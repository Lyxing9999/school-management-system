from __future__ import annotations

from functools import wraps
from time import time
import os
import traceback
from typing import Any, Dict, Optional

from flask import request, g
from pydantic import BaseModel, RootModel

from app.contexts.infra.http.responses import Response
from app.contexts.core.log.log_service import LogService
from app.contexts.core.errors.app_base_exception import AppBaseException, handle_exception
from app.contexts.common.base_response_dto import BaseResponseDTO

log_service = LogService.get_instance()

STACK_FRAMES = int(os.getenv("LOG_STACK_FRAMES", "6"))


# -----------------------
# helpers
# -----------------------
def _dump_pydantic(data: BaseModel) -> Any:
    if isinstance(data, RootModel):
        root = data.__root__
        if isinstance(root, list):
            return [x.model_dump(mode="json", exclude_none=True) for x in root]
        return root
    return data.model_dump(mode="json", exclude_none=True)


def _stack_tail(frames: int = STACK_FRAMES) -> list[str]:
    tb = traceback.extract_tb(__import__("sys").exc_info()[2])
    tail = tb[-frames:] if tb else []
    return [f"{x.filename}:{x.lineno} in {x.name}" for x in tail]


def _actor_id() -> Optional[str]:
    user = getattr(g, "user", None)
    if not user:
        return None
    uid = getattr(user, "id", None) or getattr(user, "_id", None)
    return str(uid) if uid is not None else None


def _request_id() -> Optional[str]:
    return request.headers.get("X-Request-Id") or request.headers.get("X-Correlation-Id")


def _to_str(v: Any) -> Optional[str]:
    """
    Normalize Enum-like values to plain strings.
    """
    if v is None:
        return None
    # Enum -> value
    enum_value = getattr(v, "value", None)
    if enum_value is not None:
        return str(enum_value)
    return str(v)


def _pick_error_code(e: Exception) -> str:
    """
    Ensure code is never null. Adjust precedence based on your exception design.
    """
    return (
        getattr(e, "code", None)
        or getattr(e, "error", None)
        or getattr(e, "error_code", None)
        or type(e).__name__
    )


def _minimal_headers() -> Dict[str, Any]:
    """
    Keep only what helps monitoring/correlation.
    (Authorization/Cookies are not included.)
    """
    return {
        "User-Agent": request.headers.get("User-Agent"),
        "X-Request-Id": request.headers.get("X-Request-Id"),
        "X-Correlation-Id": request.headers.get("X-Correlation-Id"),
        "X-Forwarded-For": request.headers.get("X-Forwarded-For"),
        "Origin": request.headers.get("Origin"),
        "Referer": request.headers.get("Referer"),
    }


def _build_error_extra(
    *,
    start_time: float,
    status: int,
    err: Exception,
    include_stack: bool,
) -> Dict[str, Any]:
    duration_ms = int((time() - start_time) * 1000)

    extra: Dict[str, Any] = {
        "event": "http_error",
        "http": {
            "method": request.method,
            "path": request.path,
            "status": status,
            "duration_ms": duration_ms,
            "request_id": _request_id(),
        },
        "actor_id": _actor_id(),
        "args": request.args.to_dict(),
        "json": request.get_json(silent=True),
        "headers": _minimal_headers(),
        "error": {
            "type": type(err).__name__,
            "code": _pick_error_code(err),
            "category": _to_str(getattr(err, "category", None)),
            "severity": _to_str(getattr(err, "severity", None)),
            "recoverable": getattr(err, "recoverable", None),
            "message": getattr(err, "user_message", None)
                       or getattr(err, "message", None)
                       or str(err),
            "details": getattr(err, "details", None),
        },
    }

    if include_stack:
        extra["stack"] = _stack_tail()

    return extra


# -----------------------
# decorator
# -----------------------
def wrap_response(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time()
        try:
            result = func(*args, **kwargs)

            default_message = f"{func.__name__.replace('_', ' ').title()} executed successfully"

            # BaseResponseDTO
            if isinstance(result, BaseResponseDTO):
                data = result.data
                if isinstance(data, BaseModel):
                    data = _dump_pydantic(data)
                elif isinstance(data, list) and all(isinstance(x, BaseModel) for x in data):
                    data = [x.model_dump(mode="json", exclude_none=True) for x in data]

                return Response.success_response(
                    data=data,
                    message=getattr(result, "message", default_message),
                    success=getattr(result, "success", True),
                )

            # Plain BaseModel
            if isinstance(result, BaseModel):
                return Response.success_response(
                    data=result.model_dump(mode="json", exclude_none=True),
                    message=default_message,
                    success=True,
                )

            # Plain dict/list
            if isinstance(result, (dict, list)):
                return Response.success_response(
                    data=result,
                    message=default_message,
                    success=True,
                )

            # fallback
            return Response.success_response(
                data={"result": result},
                message=default_message,
                success=True,
            )

        except AppBaseException as e:
            # Business-rule errors: small log, no stack
            status = getattr(e, "http_status", None) or 400

            log_service.log(
                "Request failed (business rule)",
                level="WARN",
                module=func.__module__,
                user_id=_actor_id(),
                extra=_build_error_extra(
                    start_time=start_time,
                    status=status,
                    err=e,
                    include_stack=False,
                ),
            )
            return Response._prepare_error_response(error=e)

        except Exception as e:
            # Unexpected errors: include short stack tail
            app_exc = handle_exception(e)
            status = getattr(app_exc, "http_status", None) or 500

            log_service.log(
                "Request failed (unexpected error)",
                level="ERROR",
                module=func.__module__,
                user_id=_actor_id(),
                extra=_build_error_extra(
                    start_time=start_time,
                    status=status,
                    err=app_exc,
                    include_stack=True,
                ),
            )
            return Response._prepare_error_response(error=app_exc)

    return wrapper