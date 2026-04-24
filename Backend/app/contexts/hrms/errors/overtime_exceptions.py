from datetime import date as date_type

from app.contexts.core.errors import AppBaseException, ErrorCategory, ErrorSeverity


class OvertimeRequestNotFoundException(AppBaseException):
    def __init__(self, overtime_request_id: str):
        super().__init__(
            message=f"Overtime request '{overtime_request_id}' not found",
            error_code="OVERTIME_NOT_FOUND",
            status_code=404,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.BUSINESS_LOGIC,
            context={"overtime_request_id": str(overtime_request_id)},
            user_message="Overtime request not found.",
            recoverable=True,
        )


class OvertimeOwnershipRequiredException(AppBaseException):
    def __init__(self, actor_id: str, overtime_employee_id: str):
        super().__init__(
            message="You can only cancel your own overtime request",
            error_code="OVERTIME_OWNERSHIP_REQUIRED",
            status_code=403,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.AUTHORIZATION,
            details={"actor_id": actor_id, "overtime_employee_id": overtime_employee_id},
            user_message="You are not allowed to cancel this overtime request.",
            recoverable=True,
        )


class InvalidOvertimeTimeRangeException(AppBaseException):
    def __init__(self):
        super().__init__(
            message="Invalid overtime time range",
            error_code="OVERTIME_TIME_RANGE_INVALID",
            status_code=400,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.VALIDATION,
            user_message="Invalid overtime time range.",
            recoverable=True,
        )


class OvertimeEndTimeInvalidException(AppBaseException):
    def __init__(self):
        super().__init__(
            message="OT end_time must be after start_time",
            error_code="OVERTIME_END_TIME_INVALID",
            status_code=400,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.VALIDATION,
            user_message="Overtime end time must be after start time.",
            recoverable=True,
        )


class InvalidLocalizedOvertimeTimeRangeException(AppBaseException):
    def __init__(self):
        super().__init__(
            message="Invalid localized overtime time range",
            error_code="OVERTIME_LOCAL_TIME_RANGE_INVALID",
            status_code=400,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.VALIDATION,
            user_message="Invalid overtime time range in local time.",
            recoverable=True,
        )


class OvertimeRequestDateMismatchException(AppBaseException):
    def __init__(self, request_date: date_type, start_date_local: date_type):
        super().__init__(
            message="request_date must match overtime start date in Cambodia time",
            error_code="OVERTIME_REQUEST_DATE_MISMATCH",
            status_code=400,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.VALIDATION,
            user_message="Request date must match the overtime start date.",
            details={
                "request_date": str(request_date),
                "start_date_local": str(start_date_local),
            },
            recoverable=True,
        )


class WorkingDayOvertimeStartInvalidException(AppBaseException):
    def __init__(self):
        super().__init__(
            message="Working day overtime must start after scheduled end time",
            error_code="OVERTIME_WORKING_DAY_START_INVALID",
            status_code=400,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="Working day overtime must start after your scheduled work shift.",
            recoverable=True,
        )


class OverlappingOvertimeRequestException(AppBaseException):
    def __init__(self, employee_id: str, request_date: date_type):
        super().__init__(
            message="Overlapping overtime request already exists",
            error_code="OVERTIME_OVERLAP_EXISTS",
            status_code=400,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="An overlapping overtime request already exists for this date.",
            details={"employee_id": employee_id, "request_date": str(request_date)},
            recoverable=True,
        )


class OvertimeReasonRequiredException(AppBaseException):
    def __init__(self):
        super().__init__(
            message="OT reason is required",
            error_code="OVERTIME_REASON_REQUIRED",
            status_code=400,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.VALIDATION,
            user_message="Overtime reason is required.",
            recoverable=True,
        )


class OvertimeBasicSalaryInvalidException(AppBaseException):
    def __init__(self):
        super().__init__(
            message="Basic salary cannot be negative",
            error_code="OVERTIME_BASIC_SALARY_INVALID",
            status_code=400,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.VALIDATION,
            user_message="Basic salary cannot be negative.",
            recoverable=True,
        )


class OvertimeSubmissionDeadlineExceededException(AppBaseException):
    def __init__(self):
        super().__init__(
            message="OT request must be submitted at least 3 hours before end of working time",
            error_code="OVERTIME_SUBMISSION_DEADLINE_EXCEEDED",
            status_code=400,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="Overtime request must be submitted at least 3 hours before the end of the work day.",
            recoverable=True,
        )


class OvertimeApprovalStateInvalidException(AppBaseException):
    def __init__(self, overtime_id: str, status: str):
        super().__init__(
            message="Only pending OT request can be approved",
            error_code="OVERTIME_APPROVAL_STATE_INVALID",
            status_code=400,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="Only pending overtime requests can be approved.",
            details={"overtime_id": overtime_id, "status": status},
            recoverable=True,
        )


class OvertimeApprovedHoursNegativeException(AppBaseException):
    def __init__(self):
        super().__init__(
            message="approved_hours cannot be negative",
            error_code="OVERTIME_APPROVED_HOURS_NEGATIVE",
            status_code=400,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.VALIDATION,
            user_message="Approved hours cannot be negative.",
            recoverable=True,
        )


class OvertimeApprovedHoursExceedsRequestedException(AppBaseException):
    def __init__(self):
        super().__init__(
            message="approved_hours cannot exceed requested hours",
            error_code="OVERTIME_APPROVED_HOURS_EXCEEDS_REQUESTED",
            status_code=400,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.VALIDATION,
            user_message="Approved hours cannot exceed requested hours.",
            recoverable=True,
        )


class OvertimeRejectionStateInvalidException(AppBaseException):
    def __init__(self, overtime_id: str, status: str):
        super().__init__(
            message="Only pending OT request can be rejected",
            error_code="OVERTIME_REJECTION_STATE_INVALID",
            status_code=400,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="Only pending overtime requests can be rejected.",
            details={"overtime_id": overtime_id, "status": status},
            recoverable=True,
        )


class OvertimeCancellationStateInvalidException(AppBaseException):
    def __init__(self, overtime_id: str, status: str):
        super().__init__(
            message="Only pending OT request can be cancelled",
            error_code="OVERTIME_CANCELLATION_STATE_INVALID",
            status_code=400,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="Only pending overtime requests can be cancelled.",
            details={"overtime_id": overtime_id, "status": status},
            recoverable=True,
        )