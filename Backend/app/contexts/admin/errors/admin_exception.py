from app.contexts.core.errors import AppBaseException, ErrorSeverity, ErrorCategory

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



class TeachingAssignmentAlreadyExistsException(AppBaseException):
    def __init__(self, *, class_id: str, subject_id: str, teacher_id: Optional[str] = None):
        details: Dict[str, Any] = {"class_id": class_id, "subject_id": subject_id}
        if teacher_id:
            details["teacher_id"] = teacher_id

        super().__init__(
            message=f"Teaching assignment already exists for class_id={class_id}, subject_id={subject_id}.",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="This subject already has a teacher assigned in this class.",
            details=details,
            hint="Use overwrite=true to replace the existing teacher assignment.",
            recoverable=True,
        )


class TeachingAssignmentNotFoundException(AppBaseException):
    def __init__(self, *, class_id: str, subject_id: str):
        super().__init__(
            message=f"Teaching assignment not found for class_id={class_id}, subject_id={subject_id}.",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="No active teacher assignment was found for this class and subject.",
            details={"class_id": class_id, "subject_id": subject_id},
            hint="Check that the class/subject IDs are correct, or that the assignment is not already unassigned.",
            recoverable=True,
        )


class InvalidTeachingAssignmentFilterException(AppBaseException):
    def __init__(self, *, field: str, value: str, allowed: list[str]):
        super().__init__(
            message=f"Invalid filter value for {field}: {value}. Allowed={allowed}",
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message=f"Invalid filter value for '{field}'.",
            details={"field": field, "value": value, "allowed": allowed},
            hint=f"Use one of: {', '.join(allowed)}",
            recoverable=True,
        )