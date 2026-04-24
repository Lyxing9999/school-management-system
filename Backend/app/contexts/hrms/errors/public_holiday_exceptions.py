from bson import ObjectId
from app.contexts.core.errors import AppBaseException, ErrorSeverity, ErrorCategory


class PublicHolidayNotFoundException(AppBaseException):
    def __init__(self, holiday_id: str):
        super().__init__(
            message=f"Public holiday '{holiday_id}' not found",
            error_code="PUBLIC_HOLIDAY_NOT_FOUND",
            status_code=404,
            user_message="Public holiday not found.",
        )