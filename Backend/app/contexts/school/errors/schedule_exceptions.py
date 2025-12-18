from app.contexts.core.error.app_base_exception import (
    AppBaseException,
    ErrorCategory,
    ErrorSeverity
)

class InvalidDayOfWeekException(AppBaseException):
    def __init__(self, received_value):
        super().__init__(
            message=f"Invalid day_of_week: {received_value}",
            error_code="SCHEDULE_INVALID_DAY",
            status_code=400,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.VALIDATION,
            user_message="The day of the week provided is not valid.",
            recoverable=True,
            received_value=received_value,
            hint="Valid values: 1 (Monday) to 7 (Sunday)."
        )


class InvalidScheduleTimeException(AppBaseException):
    def __init__(self):
        super().__init__(
            message="start_time and end_time must be datetime.time instances",
            error_code="SCHEDULE_INVALID_TIME",
            status_code=400,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.VALIDATION,
            user_message="Start and end times must be valid time objects.",
            recoverable=True,
            hint="Use Python datetime.time objects for start_time and end_time."
        )


class StartTimeAfterEndTimeException(AppBaseException):
    def __init__(self, start_time, end_time):
        super().__init__(
            message=f"start_time {start_time} must be before end_time {end_time}",
            error_code="SCHEDULE_START_AFTER_END",
            status_code=400,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="The start time must be before the end time.",
            recoverable=True,
            context={"start_time": str(start_time), "end_time": str(end_time)},
            hint="Adjust start_time and end_time to avoid overlap."
        )


class ScheduleNotFoundException(AppBaseException):
    def __init__(self, oid):
        super().__init__(
            message=f"Schedule not found for ID: {oid}",
            error_code="SCHEDULE_NOT_FOUND",
            status_code=404,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.NOT_FOUND,
            user_message="The schedule was not found.",
            recoverable=True,
            context={"schedule_id": str(oid)},
            hint="Verify the schedule ID and try again."
        )

class ScheduleUpdateFailedException(AppBaseException):
    def __init__(self, oid):
        super().__init__(
            message=f"Schedule update failed for ID: {oid}",
            error_code="SCHEDULE_UPDATE_FAILED",
            status_code=500,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="The schedule update failed.",
            recoverable=True,
            context={"schedule_id": str(oid)},
            hint="Verify the schedule ID and try again."
        )