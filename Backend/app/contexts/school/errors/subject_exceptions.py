from app.contexts.core.error import AppBaseException, ErrorSeverity, ErrorCategory


from app.contexts.core.error import AppBaseException, ErrorSeverity, ErrorCategory


class SubjectError(AppBaseException):
    """Base class for all Subject domain errors."""
    def __init__(self, message: str, **kwargs):
        severity = kwargs.pop("severity", ErrorSeverity.MEDIUM)

        super().__init__(
            message=message,
            category=ErrorCategory.BUSINESS_LOGIC,
            severity=severity,
            **kwargs
        )
class InvalidSubjectNameError(SubjectError):
    def __init__(self, received_value: str):
        super().__init__(
            message="Subject name cannot be empty.",
            error_code="SUBJECT_INVALID_NAME",
            severity=ErrorSeverity.LOW,
            received_value=received_value,
            hint="Provide a non-empty subject name."
        )


class InvalidSubjectCodeError(SubjectError):
    def __init__(self, received_value: str):
        super().__init__(
            message="Subject code cannot be empty.",
            error_code="SUBJECT_INVALID_CODE",
            severity=ErrorSeverity.LOW,
            received_value=received_value,
            hint="Provide a non-empty subject code."
        )


class InvalidGradeLevelError(SubjectError):
    def __init__(self, level: int):
        super().__init__(
            message=f"Invalid grade level: {level}.",
            error_code="SUBJECT_INVALID_GRADE_LEVEL",
            severity=ErrorSeverity.LOW,
            received_value=level,
            hint="Grade levels must be between 1 and 12."
        )




class SubjectCodeAlreadyExistsException(SubjectError):
    """Raised when a subject code already exists in the system."""
    def __init__(self, received_value: str):
        super().__init__(
            message=f"Subject code '{received_value}' already exists.",
            error_code="SUBJECT_CODE_ALREADY_EXISTS",
            severity=ErrorSeverity.LOW,
            received_value=received_value,
            hint="Choose a unique subject code that does not exist in the system."
        )


class SubjectNameAlreadyExistsException(SubjectError):
    """Raised when a subject name already exists in the system."""
    def __init__(self, received_value: str):
        super().__init__(
            message=f"Subject name '{received_value}' already exists.",
            error_code="SUBJECT_NAME_ALREADY_EXISTS",
            severity=ErrorSeverity.LOW,
            received_value=received_value,
            hint="Choose a unique subject name that does not exist in the system."
        )