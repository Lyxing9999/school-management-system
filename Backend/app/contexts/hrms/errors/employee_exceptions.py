# app/contexts/hrms/errors/employee_exceptions.py
from bson import ObjectId
from datetime import date as date_type
from app.contexts.core.errors import AppBaseException, ErrorSeverity, ErrorCategory

class EmployeeNotFoundException(AppBaseException):
    def __init__(self, employee_id: str):
        super().__init__(
            message=f"Employee '{employee_id}' not found",
            error_code="EMPLOYEE_NOT_FOUND",
            status_code=404,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="Employee not found.",
            context={"employee_id": employee_id},
            recoverable=True,
        )

class EmployeeDeletedException(AppBaseException):
    def __init__(self, employee_id: ObjectId):
        super().__init__(
            message=f"Employee {employee_id} is deleted",
            error_code="EMPLOYEE_DELETED",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="This employee has been deleted.",
            details={"employee_id": str(employee_id)},
            hint="Restore employee before linking account",
            recoverable=True,
        )

class EmployeeCodeAlreadyExistsException(AppBaseException):
    def __init__(self, employee_code: str):
        super().__init__(
            message=f"Employee code '{employee_code}' already exists",
            error_code="EMPLOYEE_CODE_EXISTS",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="Employee code already exists.",
            details={"employee_code": employee_code},
            recoverable=True,
        )

class ContractRequiredException(AppBaseException):
    def __init__(self, employee_id: ObjectId):
        super().__init__(
            message="Contract is required for contract employees",
            error_code="EMPLOYEE_CONTRACT_REQUIRED",
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.VALIDATION,
            user_message="A contract is required for this employee type.",
            details={"employee_id": str(employee_id)},
            recoverable=True,
        )

class ContractDateInvalidException(AppBaseException):
    def __init__(self, start_date: date_type | None, end_date: date_type | None):
        super().__init__(
            message=f"Invalid contract dates: {start_date} -> {end_date}",
            error_code="EMPLOYEE_CONTRACT_DATE_INVALID",
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.VALIDATION,
            user_message="Invalid contract date range provided.",
            details={"start_date": str(start_date), "end_date": str(end_date)},
            hint="contract.end_date must be >= contract.start_date",
            recoverable=True,
        )


class EmployeeInactiveException(AppBaseException):
    def __init__(self, employee_id: str, status: str):
        super().__init__(
            message=f"Employee '{employee_id}' is not active (status={status})",
            error_code="EMPLOYEE_INACTIVE",
            status_code=403,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="Employee account is not active.",
            details={"employee_id": employee_id, "status": status},
            hint="Activate employee status before attendance operations.",
            recoverable=True,
        )


class EmployeeScheduleNotAssignedException(AppBaseException):
    def __init__(self, employee_id: str):
        super().__init__(
            message=f"Employee '{employee_id}' has no assigned working schedule",
            error_code="EMPLOYEE_SCHEDULE_NOT_ASSIGNED",
            status_code=400,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="Working schedule is required before attendance operations.",
            details={"employee_id": employee_id},
            hint="Assign a working schedule to the employee.",
            recoverable=True,
        )


class EmployeeLinkedAccountNotFoundException(AppBaseException):
    def __init__(self, user_id: str):
        super().__init__(
            message=f"Linked IAM account '{user_id}' not found",
            error_code="EMPLOYEE_LINKED_ACCOUNT_NOT_FOUND",
            status_code=404,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="The selected account was not found.",
            details={"user_id": user_id},
            hint="Verify the account id exists in IAM before linking.",
            recoverable=True,
        )


class EmployeeLinkedAccountRoleNotAllowedException(AppBaseException):
    def __init__(self, role: str, allowed_roles: list[str]):
        super().__init__(
            message=(
                f"Account role '{role}' is not allowed for employee link. "
                f"Allowed roles: {allowed_roles}"
            ),
            error_code="EMPLOYEE_LINKED_ACCOUNT_ROLE_NOT_ALLOWED",
            status_code=400,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="The selected account role is not allowed for employee linking.",
            details={"role": role, "allowed_roles": allowed_roles},
            hint="Use one of the allowed HRMS roles for the linked account.",
            recoverable=True,
        )


class EmployeeAccountAlreadyLinkedException(AppBaseException):
    def __init__(self, user_id: str, linked_employee_id: str):
        super().__init__(
            message=(
                f"Account '{user_id}' is already linked to employee '{linked_employee_id}'"
            ),
            error_code="EMPLOYEE_ACCOUNT_ALREADY_LINKED",
            status_code=409,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="This account is already linked to another employee.",
            details={"user_id": user_id, "linked_employee_id": linked_employee_id},
            hint="Unlink the account from the current employee before linking it again.",
            recoverable=True,
        )


class EmployeeAlreadyHasLinkedAccountException(AppBaseException):
    def __init__(self, employee_id: str):
        super().__init__(
            message=f"Employee '{employee_id}' already has an IAM account linked",
            error_code="EMPLOYEE_ALREADY_HAS_LINKED_ACCOUNT",
            status_code=409,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="This employee already has an account linked.",
            details={"employee_id": employee_id},
            hint="Use a different employee or unlink the existing account first.",
            recoverable=True,
        )


class EmployeeIamAccountCreationFailedException(AppBaseException):
    def __init__(self, employee_id: str):
        super().__init__(
            message=f"Failed to create IAM account for employee '{employee_id}'",
            error_code="EMPLOYEE_IAM_ACCOUNT_CREATION_FAILED",
            status_code=500,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.SYSTEM,
            user_message="Unable to create account for employee.",
            details={"employee_id": employee_id},
            hint="Verify IAM service availability and retry the operation.",
            recoverable=True,
        )


class EmployeeAccountLinkConflictException(AppBaseException):
    def __init__(self, employee_id: str):
        super().__init__(
            message=f"Employee '{employee_id}' could not be linked because the account is already claimed",
            error_code="EMPLOYEE_ACCOUNT_LINK_CONFLICT",
            status_code=409,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="This employee already has an account linked.",
            details={"employee_id": employee_id},
            hint="Verify the employee has not been linked by another process.",
            recoverable=True,
        )


class EmployeeLinkedAccountRequiredException(AppBaseException):
    def __init__(self, employee_id: str):
        super().__init__(
            message=f"Employee '{employee_id}' has no linked IAM account",
            error_code="EMPLOYEE_LINKED_ACCOUNT_REQUIRED",
            status_code=400,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="Employee has no linked account.",
            details={"employee_id": employee_id},
            hint="Link an IAM account to the employee before changing password.",
            recoverable=True,
        )