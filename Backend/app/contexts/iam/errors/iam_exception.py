from typing import Any, Dict
from app.contexts.core.errors import AppBaseException, ErrorSeverity, ErrorCategory

class UsernameAlreadyExistsException(AppBaseException):
    def __init__(self, username: str):
        super().__init__(
            message=f"Username '{username}' already exists",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="This username is already taken. Please choose another.",
            details={"field": "username", "value": username},
            hint="Consider appending a number or variation to the username",
            recoverable=True
        )


        
class InvalidPasswordException(AppBaseException):
    def __init__(self, password: str):
        super().__init__(
            message=f"Invalid password provided",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="The password is incorrect.",
            details={"field": "password", "value": password},
            hint="Password must meet the required complexity rules",
            recoverable=True 
        )


class InvalidRoleException(AppBaseException):
    def __init__(self, role: str):
        super().__init__(
            message=f"Invalid role '{role}' attempted",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message=f"The role '{role}' is not allowed. Please choose another.",
            details={"field": "role", "value": role},
            hint="Check available roles and permissions",
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


class RoleNotAllowedException(AppBaseException):
    def __init__(self, role: str):
        super().__init__(
            message=f"Role '{role}' is not allowed",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message=f"The role '{role}' cannot be assigned.",
            details={"field": "role", "value": role},
            hint="Assign a valid role from the allowed list",
            recoverable=True
        )


class NotFoundUserException(AppBaseException):
    def __init__(self, identifier: str):
        super().__init__(
            message=f"User '{identifier}' not found",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="The requested user does not exist.",
            details={"field": "identifier", "value": identifier},
            hint="Verify the user ID or create the user if missing",
            recoverable=True
        )


class NoChangeAppException(AppBaseException):
    def __init__(self):
        super().__init__(
            message="No changes to apply",
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.INFO,
            user_message="No changes were detected to update.",
            hint="Ensure you have modified fields before submitting",
            recoverable=True
        )


class AppTypeError(AppBaseException):
    def __init__(self, type_name: str = "", received_value: Any = None, user_message: str = ""):
        super().__init__(
            message=f"Invalid input type '{type_name}'",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message=user_message,
            details={"type": type_name, "value": received_value},
            hint=f"Ensure the input matches the expected type: {type_name}",
            recoverable=True
        )

class AuthServiceRequiredException(AppBaseException):
    def __init__(self):
        super().__init__(
            message="Auth service is required",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="Authentication service is required for this operation.",
            hint="Ensure the auth service is provided before performing the operation",
            recoverable=True
        )

class PydanticBaseValidationError(AppBaseException):

    def __init__(self, field_errors: Dict[str, str], message: str = "Validation failed", cause: Exception = None, context: str = "single"):
        super().__init__(
            message=message,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.VALIDATION,
            user_message="One or more fields are invalid. Please check your input.",
            details={"field_errors": field_errors, "context": context},
            hint="Correct the input fields as indicated in 'field_errors'",
            recoverable=True,  
        )
        self.cause = cause
        self.field_errors = field_errors
        self.context = context

class InvalidUserDataException(AppBaseException):
    def __init__(self, user_data: Dict[str, Any]):
        super().__init__(
            message="Invalid user data provided",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="The provided user data is invalid. Please check your input.",
            details={"user_data": user_data},
            hint="Correct the input fields as indicated in 'user_data'",
            recoverable=True,

        )

class UserDeletedException(AppBaseException):
    def __init__(self, email: str):
        super().__init__(
            message=f"User with email '{email}' is deleted",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="The requested user is deleted.",
            details={"email": email},
            hint="Verify the user ID or create the user if missing",
            recoverable=True
        )
    

class UnknownRoleException(AppBaseException):
    def __init__(self, role: str):
        super().__init__(
            message=f"Unknown role '{role}'",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="The requested role is unknown.",
            details={"role": role},
            hint="Verify the role or create the role if missing",
            recoverable=True
        )

class RoleNotAllowedException(AppBaseException):
    def __init__(self, role: str):
        super().__init__(
            message=f"Role '{role}' is not allowed",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message=f"The role '{role}' cannot be assigned.",
            details={"field": "role", "value": role},
            hint="Assign a valid role from the allowed list",
            recoverable=True
        )
    


class UserNotSavedException(AppBaseException):
    def __init__(self, user_id: str):
        super().__init__(
            message=f"User with ID '{user_id}' not saved",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="The requested user is not saved.",
            details={"user_id": user_id},
            hint="Verify the user ID or create the user if missing",
            recoverable=True
        )


    



class UserDeletedException(AppBaseException):
    def __init__(self, identifier: str):
        super().__init__(
            message=f"User '{identifier}' is deleted",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="This account is not available.",
            details={"identifier": identifier},
            hint="Restore the account if this is a mistake.",
            recoverable=True,
        )
class UserInactiveException(AppBaseException):
    def __init__(self, identifier: str, status: str = "inactive"):
        super().__init__(
            message=f"User '{identifier}' is inactive (status={status})",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="Your account is inactive. Please contact an administrator.",
            details={"identifier": identifier, "status": status},
            hint="Set user status back to 'active' to allow login.",
            recoverable=True,
        )


class UserSuspendedException(AppBaseException):
    def __init__(self, identifier: str):
        super().__init__(
            message=f"User '{identifier}' is suspended",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="Your account has been suspended. Please contact support.",
            details={"identifier": identifier, "status": "suspended"},
            hint="Remove suspension (set status to 'active') to allow login.",
            recoverable=True,
        )