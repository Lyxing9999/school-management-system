from app.contexts.core.errors import AppBaseException, ErrorCategory, ErrorSeverity


class AttendanceNotFoundException(AppBaseException):
    def __init__(self, attendance_id):
        super().__init__(
            message=f"Attendance record with ID '{attendance_id}' was not found",
            error_code="ATTENDANCE_NOT_FOUND",
            status_code=404,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="Attendance record not found.",
            details={"attendance_id": str(attendance_id)},
            recoverable=True,
        )


class AttendanceDeletedException(AppBaseException):
    def __init__(self, attendance_id):
        super().__init__(
            message=f"Attendance record '{attendance_id}' has already been deleted",
            error_code="ATTENDANCE_DELETED",
            status_code=410,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="Attendance record is deleted.",
            details={"attendance_id": str(attendance_id)},
            recoverable=True,
        )


class AttendanceAlreadyCheckedOutException(AppBaseException):
    def __init__(self, attendance_id):
        super().__init__(
            message=f"Attendance '{attendance_id}' already has check-out data",
            error_code="ATTENDANCE_ALREADY_CHECKED_OUT",
            status_code=400,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="Employee has already checked out.",
            details={"attendance_id": str(attendance_id)},
            recoverable=True,
        )


class InvalidCheckOutTimeException(AppBaseException):
    def __init__(self, attendance_id):
        super().__init__(
            message=f"Check-out time is earlier than check-in time for attendance '{attendance_id}'",
            error_code="INVALID_CHECK_OUT_TIME",
            status_code=400,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.VALIDATION,
            user_message="Check-out time cannot be before check-in time.",
            details={"attendance_id": str(attendance_id)},
            hint="Send a check-out time equal to or later than check-in time.",
            recoverable=True,
        )


class AlreadyCheckedInTodayException(AppBaseException):
    def __init__(self, employee_id):
        super().__init__(
            message=f"Employee '{employee_id}' already has attendance for today",
            error_code="ALREADY_CHECKED_IN_TODAY",
            status_code=400,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="You have already checked in today.",
            details={"employee_id": str(employee_id)},
            recoverable=True,
        )


class AttendanceCheckInRequiredException(AppBaseException):
    def __init__(self, employee_id):
        super().__init__(
            message=f"Employee '{employee_id}' cannot check out without a check-in record for today",
            error_code="ATTENDANCE_CHECK_IN_REQUIRED",
            status_code=400,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="Check-in is required before check-out.",
            details={"employee_id": str(employee_id)},
            hint="Submit a check-in first for the same attendance date.",
            recoverable=True,
        )


class AttendanceWrongLocationReviewStateException(AppBaseException):
    def __init__(self, attendance_id, current_status: str):
        super().__init__(
            message=(
                f"Attendance '{attendance_id}' is not pending wrong-location review "
                f"(current_status='{current_status}')"
            ),
            error_code="ATTENDANCE_WRONG_LOCATION_REVIEW_STATE_INVALID",
            status_code=400,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="Attendance is not waiting for wrong-location review.",
            details={
                "attendance_id": str(attendance_id),
                "current_status": current_status,
            },
            hint="Only attendance with location_review_status='pending' can be reviewed.",
            recoverable=True,
        )


class AttendanceEarlyLeaveReviewStateException(AppBaseException):
    def __init__(self, attendance_id, current_status: str):
        super().__init__(
            message=(
                f"Attendance '{attendance_id}' is not pending early-leave review "
                f"(current_status='{current_status}')"
            ),
            error_code="ATTENDANCE_EARLY_LEAVE_REVIEW_STATE_INVALID",
            status_code=400,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="Attendance is not waiting for early-leave review.",
            details={
                "attendance_id": str(attendance_id),
                "current_status": current_status,
            },
            hint="Only attendance with early_leave_review_status='pending' can be reviewed.",
            recoverable=True,
        )


class LocationValidationException(AppBaseException):
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(
            message=message,
            error_code="ATTENDANCE_LOCATION_VALIDATION_FAILED",
            status_code=400,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.VALIDATION,
            user_message="Location validation failed for attendance.",
            details=details or {},
            recoverable=True,
        )


class NotScheduledWorkingDayException(AppBaseException):
    def __init__(self, employee_id, weekday_value: int):
        super().__init__(
            message=(
                f"Employee '{employee_id}' attempted attendance on non-working weekday "
                f"index {weekday_value}"
            ),
            error_code="NOT_SCHEDULED_WORKING_DAY",
            status_code=400,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="Today is not part of your configured working days.",
            details={"employee_id": str(employee_id), "weekday": weekday_value},
            recoverable=True,
        )


class InvalidLateMinutesException(AppBaseException):
    def __init__(self, late_minutes: int):
        super().__init__(
            message=f"late_minutes cannot be negative (received={late_minutes})",
            error_code="INVALID_LATE_MINUTES",
            status_code=400,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.VALIDATION,
            user_message="Late minutes must be zero or greater.",
            details={"late_minutes": late_minutes},
            recoverable=True,
        )


class LateReasonRequiredException(AppBaseException):
    def __init__(self, employee_id):
        super().__init__(
            message=(
                f"late_reason is required when employee '{employee_id}' checks in late"
            ),
            error_code="LATE_REASON_REQUIRED",
            status_code=400,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.VALIDATION,
            user_message="Please provide a reason for late check-in.",
            details={"employee_id": str(employee_id)},
            recoverable=True,
        )


class EarlyLeaveReasonRequiredException(AppBaseException):
    def __init__(self, employee_id):
        super().__init__(
            message=(
                f"early_leave_reason is required when employee '{employee_id}' checks out early"
            ),
            error_code="EARLY_LEAVE_REASON_REQUIRED",
            status_code=400,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.VALIDATION,
            user_message="Please provide a reason for early check-out.",
            details={"employee_id": str(employee_id)},
            recoverable=True,
        )


class UnpaidPublicHolidayCheckInNotAllowedException(AppBaseException):
    def __init__(self, employee_id, holiday_date: str):
        super().__init__(
            message=(
                f"Employee '{employee_id}' cannot check in on unpaid public holiday date {holiday_date}"
            ),
            error_code="UNPAID_PUBLIC_HOLIDAY_CHECK_IN_NOT_ALLOWED",
            status_code=400,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="Check-in is not allowed on an unpaid public holiday.",
            details={
                "employee_id": str(employee_id),
                "holiday_date": holiday_date,
            },
            recoverable=True,
        )
