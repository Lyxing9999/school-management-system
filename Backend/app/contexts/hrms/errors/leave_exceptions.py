# app/contexts/hrms/errors/leave_exceptions.py
from datetime import date as date_type
from bson import ObjectId
from app.contexts.core.errors import AppBaseException, ErrorSeverity, ErrorCategory

class LeaveDateRangeInvalidException(AppBaseException):
    def __init__(self, start_date: date_type, end_date: date_type):
        super().__init__(
            message=f"Invalid leave range: {start_date} -> {end_date}",
            error_code="LEAVE_RANGE_INVALID",
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="Invalid leave date range provided.",
            details={"start_date": str(start_date), "end_date": str(end_date)},
            hint="end_date must be >= start_date",
            recoverable=True,
        )

class LeaveOutsideContractException(AppBaseException):
    def __init__(self, start_date: date_type, end_date: date_type, cstart: date_type, cend: date_type):
        super().__init__(
            message=f"Leave {start_date}->{end_date} outside contract {cstart}->{cend}",
            error_code="LEAVE_OUTSIDE_CONTRACT",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="Leave dates are outside of the contract period.",
            details={"leave_start": str(start_date), "leave_end": str(end_date), "contract_start": str(cstart), "contract_end": str(cend)},
            hint="Leave dates must be within contract period",
            recoverable=True,
        )

class LeaveAlreadyReviewedException(AppBaseException):
    def __init__(self, leave_id: ObjectId, status: str):
        super().__init__(
            message=f"Leave {leave_id} already reviewed (status={status})",
            error_code="LEAVE_ALREADY_REVIEWED",
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message=f"This leave request has already been reviewed (status: {status}).",
            details={"leave_id": str(leave_id), "status": status},
            hint="Only pending leave can be approved/rejected/cancelled",
            recoverable=True,
        )

class LeaveRequestDeletedException(AppBaseException):
    def __init__(self, leave_id: ObjectId):
        super().__init__(
            message=f"Leave {leave_id} is deleted",
            error_code="LEAVE_DELETED",
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="This leave request has been deleted.",
            details={"leave_id": str(leave_id)},
            hint="Restore leave or create new leave",
            recoverable=True,
        )

class LeaveNotFoundException(AppBaseException):
    def __init__(self, leave_id: str):
        super().__init__(
            message=f"Leave {leave_id} not found",
            error_code="LEAVE_NOT_FOUND",
            status_code=404,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.BUSINESS_LOGIC,
            context={"leave_id": leave_id},
            user_message="The requested leave does not exist.",
            hint="Check leave ID",
            recoverable=True,
        )


class LeaveEmployeeNotFoundException(AppBaseException):
    def __init__(self, employee_id: str):
        super().__init__(
            message="Employee not found",
            error_code="LEAVE_EMPLOYEE_NOT_FOUND",
            status_code=404,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.BUSINESS_LOGIC,
            context={"employee_id": employee_id},
            user_message="Employee not found.",
            hint="Check employee ID linked to the leave request",
            recoverable=True,
        )


class LeaveApprovalNotAllowedException(AppBaseException):
    def __init__(self, manager_user_id: str, employee_manager_user_id: str):
        super().__init__(
            message="You can only approve leave requests from your own team",
            error_code="LEAVE_APPROVAL_NOT_ALLOWED",
            status_code=403,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.AUTHORIZATION,
            details={
                "manager_user_id": manager_user_id,
                "employee_manager_user_id": employee_manager_user_id,
            },
            user_message="You are not allowed to approve this leave request.",
            hint="Only the employee's manager can approve this leave request",
            recoverable=True,
        )


class LeaveReasonRequiredException(AppBaseException):
    def __init__(self):
        super().__init__(
            message="Leave reason is required",
            error_code="LEAVE_REASON_REQUIRED",
            status_code=400,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.VALIDATION,
            user_message="Leave reason is required.",
            hint="Provide a non-empty reason for the leave request",
            recoverable=True,
        )


class LeaveOverlapExistsException(AppBaseException):
    def __init__(self, employee_id: str, start_date: date_type, end_date: date_type):
        super().__init__(
            message="Overlapping leave request already exists",
            error_code="LEAVE_OVERLAP_EXISTS",
            status_code=400,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.BUSINESS_LOGIC,
            details={
                "employee_id": employee_id,
                "start_date": str(start_date),
                "end_date": str(end_date),
            },
            user_message="An overlapping leave request already exists.",
            hint="Adjust the leave date range or cancel existing overlapping leave",
            recoverable=True,
        )


class LeaveCancellationNotAllowedException(AppBaseException):
    def __init__(self, actor_employee_id: str, leave_employee_id: str):
        super().__init__(
            message="You can only cancel your own leave request",
            error_code="LEAVE_CANCELLATION_NOT_ALLOWED",
            status_code=403,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.AUTHORIZATION,
            details={
                "actor_employee_id": actor_employee_id,
                "leave_employee_id": leave_employee_id,
            },
            user_message="You are not allowed to cancel this leave request.",
            hint="Only the owner of the leave request can cancel it",
            recoverable=True,
        )


class LeaveContractPeriodRequiredException(AppBaseException):
    def __init__(self, employee_id: str):
        super().__init__(
            message="Employee contract period is required for contract employees",
            error_code="LEAVE_CONTRACT_PERIOD_REQUIRED",
            status_code=400,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.BUSINESS_LOGIC,
            details={"employee_id": employee_id},
            user_message="Contract period is required for contract employees.",
            hint="Provide both contract start_date and end_date",
            recoverable=True,
        )


class LeaveApprovalStateInvalidException(AppBaseException):
    def __init__(self, leave_id: str, status: str):
        super().__init__(
            message="Only pending leave request can be approved",
            error_code="LEAVE_APPROVAL_STATE_INVALID",
            status_code=400,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.BUSINESS_LOGIC,
            details={"leave_id": leave_id, "status": status},
            user_message="Only pending leave can be approved.",
            recoverable=True,
        )


class LeaveRejectionStateInvalidException(AppBaseException):
    def __init__(self, leave_id: str, status: str):
        super().__init__(
            message="Only pending leave request can be rejected",
            error_code="LEAVE_REJECTION_STATE_INVALID",
            status_code=400,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.BUSINESS_LOGIC,
            details={"leave_id": leave_id, "status": status},
            user_message="Only pending leave can be rejected.",
            recoverable=True,
        )


class LeaveCancellationStateInvalidException(AppBaseException):
    def __init__(self, leave_id: str, status: str):
        super().__init__(
            message="Only pending leave request can be cancelled",
            error_code="LEAVE_CANCELLATION_STATE_INVALID",
            status_code=400,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.BUSINESS_LOGIC,
            details={"leave_id": leave_id, "status": status},
            user_message="Only pending leave can be cancelled.",
            recoverable=True,
        )