from app.contexts.core.error import AppBaseException, ErrorSeverity, ErrorCategory

class StaffNotFoundException(AppBaseException):
    def __init__(self, role: str):
        super().__init__(
            message=f"Staff not found for role: {role}",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message=f"The staff for role '{role}' was not found.",
            details={"field": "role", "value": role},
            recoverable=True
        )


class NoChangeAppException(AppBaseException):
    def __init__(self):
        super().__init__(
            message="No changes made to the user.",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="No changes made to the user.",
            details={"field": "user", "value": "No changes made to the user."},
            recoverable=True
        )
    

class EmailAlreadyExistsException(AppBaseException):
    def __init__(self, email: str):
        super().__init__(
            message=f"Email '{email}' already exists",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="This email is already registered. Please use another.",
            details={"field": "email", "value": email},
            hint="Ensure the email is unique and correctly formatted",
            recoverable=True
        )




class CannotDeleteUserInUseException(AppBaseException):
    def __init__(self, type: str, count: int):
        super().__init__(
            message=f"Cannot delete this user because they are still assigned to {count} {type}.",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message=f"Cannot delete this user because they are still assigned to {count} {type}.",
            details={"field": "user", "value": f"Cannot delete this user because they are still assigned to {count} {type}."},
            recoverable=True
        )