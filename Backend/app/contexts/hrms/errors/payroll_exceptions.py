    # app/contexts/hrms/errors/payroll_exceptions.py
from bson import ObjectId
from app.contexts.core.errors import AppBaseException, ErrorSeverity, ErrorCategory

class PayrollAlreadyFinalizedException(AppBaseException):
    def __init__(self, payroll_run_id: ObjectId, status: str):
        super().__init__(
            message=f"Payroll run {payroll_run_id} cannot be changed (status={status})",
            error_code="PAYROLL_ALREADY_FINALIZED",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message=f"Payroll run has already been finalized (status: {status}).",
            details={"payroll_run_id": str(payroll_run_id), "status": status},
            hint="Only draft payroll can be recalculated/finalized",
            recoverable=True,
        )


class PayrollRunAlreadyExistsException(AppBaseException):
    def __init__(self, month: str):
        super().__init__(
            message=f"Payroll run already exists for month {month}",
            error_code="PAYROLL_RUN_ALREADY_EXISTS",
            status_code=409,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.BUSINESS_LOGIC,
            context={"month": month},
            user_message="Payroll for this month already exists.",
            recoverable=True,
        )

class PayrollRunDeletedException(AppBaseException):
    def __init__(self, payroll_run_id: ObjectId):
        super().__init__(
            message=f"Payroll run {payroll_run_id} is deleted",
            error_code="PAYROLL_RUN_DELETED",
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="This payroll run has been deleted.",
            details={"payroll_run_id": str(payroll_run_id)},
            hint="Restore payroll run or generate a new one",
            recoverable=True,
        )

class PayrollNotFoundException(AppBaseException):
    def __init__(self, payroll_run_id: str):
        super().__init__(
            message=f"Payroll run {payroll_run_id} not found",
            error_code="PAYROLL_NOT_FOUND",
            status_code=404,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.BUSINESS_LOGIC,
            context={"payroll_run_id": payroll_run_id},
            user_message="Payroll run not found",
            hint="Generate payroll first",
            recoverable=True,
        )



class PayrollRunNotFoundException(AppBaseException):
    def __init__(self, payroll_run_id: str):
        super().__init__(
            message="Payroll run not found",
            error_code="PAYROLL_RUN_NOT_FOUND",
            status_code=404,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="Payroll run not found.",
            context={"payroll_run_id": str(payroll_run_id)},
            recoverable=True,
        )


class PayslipNotFoundException(AppBaseException):
    def __init__(self, payslip_id: str):
        super().__init__(
            message="Payslip not found",
            error_code="PAYSLIP_NOT_FOUND",
            status_code=404,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="Payslip not found.",
            context={"payslip_id": str(payslip_id)},
            recoverable=True,
        )


class PayrollMonthRequiredException(AppBaseException):
    def __init__(self):
        super().__init__(
            message="Payroll month is required",
            error_code="PAYROLL_MONTH_REQUIRED",
            status_code=400,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.VALIDATION,
            user_message="Payroll month is required.",
            recoverable=True,
        )


class PayrollFinalizeStateInvalidException(AppBaseException):
    def __init__(self, payroll_run_id: str, status: str):
        super().__init__(
            message="Only draft payroll run can be finalized",
            error_code="PAYROLL_FINALIZE_STATE_INVALID",
            status_code=400,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="Only draft payroll runs can be finalized.",
            details={"payroll_run_id": payroll_run_id, "status": status},
            recoverable=True,
        )


class PayrollMarkPaidStateInvalidException(AppBaseException):
    def __init__(self, payroll_run_id: str, status: str):
        super().__init__(
            message="Only finalized payroll run can be marked paid",
            error_code="PAYROLL_MARK_PAID_STATE_INVALID",
            status_code=400,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="Only finalized payroll runs can be marked as paid.",
            details={"payroll_run_id": payroll_run_id, "status": status},
            recoverable=True,
        )


class PayslipMonthRequiredException(AppBaseException):
    def __init__(self):
        super().__init__(
            message="Payslip month is required",
            error_code="PAYSLIP_MONTH_REQUIRED",
            status_code=400,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.VALIDATION,
            user_message="Payslip month is required.",
            recoverable=True,
        )


class PayrollExpectedWorkingDaysInvalidException(AppBaseException):
    def __init__(self, expected_working_days: int):
        super().__init__(
            message="expected_working_days must be positive",
            error_code="PAYROLL_EXPECTED_WORKING_DAYS_INVALID",
            status_code=400,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.VALIDATION,
            user_message="Expected working days must be positive.",
            details={"expected_working_days": expected_working_days},
            recoverable=True,
        )