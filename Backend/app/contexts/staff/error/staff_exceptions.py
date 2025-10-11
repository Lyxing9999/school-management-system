from app.contexts.core.error import AppBaseException, ErrorSeverity, ErrorCategory




class StaffAlreadyExistsException(AppBaseException):
    def __init__(self, staff_id: str):
        super().__init__(
            message=f"Staff with ID '{staff_id}' already exists",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="This staff ID is already registered. Please use another.",
            details={"field": "staff_id", "value": staff_id},
            hint="Ensure the staff ID is unique and correctly formatted",
            recoverable=True
        )

class StaffPermissionException(AppBaseException):
    def __init__(self, role: str):
        super().__init__(
            message=f"Staff with ID '{staff_id}' does not have permission to perform this action",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="You do not have permission to perform this action.",
            details={"field": "staff_id", "value": staff_id},
            hint="Ensure the staff ID is unique and correctly formatted",
            recoverable=True
        )


class InvalidStaffRoleException(AppBaseException):
    def __init__(self, role):
        super().__init__(
            message=f"Invalid role for Staff creation: {role}",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="The role assigned is invalid."
        )


    

class NoChangeAppException(AppBaseException):
    def __init__(self, message: str = "No changes made to the staff."):
        super().__init__(
            message=message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message=message
        )
    

class StaffNotFoundException(AppBaseException):
    def __init__(self, staff_id: str):
        super().__init__(
            message=f"Staff with ID '{staff_id}' not found",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message=f"The staff ID '{staff_id}' is not found."
        )

class StaffMissingFieldsException(AppBaseException):
    def __init__(self, message: str = "No changes made to the staff."):
        super().__init__(
            message=message,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.VALIDATION,
            user_message=message,
            hint="Ensure all required fields are provided",
            recoverable=True
        )

class StaffNoChangeAppException(AppBaseException):
    def __init__(self, message: str = "No changes made to the staff."):
        super().__init__(
            message=message,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message=message,
            hint="Ensure all required fields are provided",
            recoverable=True
        )