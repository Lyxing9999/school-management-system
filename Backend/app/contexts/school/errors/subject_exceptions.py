from app.contexts.core.errors import AppBaseException, ErrorSeverity, ErrorCategory
from bson import ObjectId

class InvalidSubjectNameError(AppBaseException):
    def __init__(self, received_value: str):
        super().__init__(
            message="Subject name cannot be empty.",
            error_code="SUBJECT_INVALID_NAME",
            severity=ErrorSeverity.LOW,
            received_value=received_value,
            user_message="Subject name cannot be empty.",
            hint="Provide a non-empty subject name."
        )


class InvalidSubjectCodeError(AppBaseException):
    def __init__(self, received_value: str):
        super().__init__(
            message="Subject code cannot be empty.",
            error_code="SUBJECT_INVALID_CODE",
            severity=ErrorSeverity.LOW,
            received_value=received_value,
            user_message="Subject code cannot be empty.",
            hint="Provide a non-empty subject code."
        )


class InvalidGradeLevelError(AppBaseException):
    def __init__(self, level: int):
        super().__init__(
            message=f"Invalid grade level: {level}.",
            error_code="SUBJECT_INVALID_GRADE_LEVEL",
            severity=ErrorSeverity.LOW,
            received_value=level,
            user_message="Invalid grade level.",
            hint="Grade levels must be between 1 and 12."
        )




class SubjectCodeAlreadyExistsException(AppBaseException):
    """Raised when a subject code already exists in the system."""
    def __init__(self, received_value: str):
        super().__init__(
            message=f"Subject code '{received_value}' already exists.",
            error_code="SUBJECT_CODE_ALREADY_EXISTS",
            severity=ErrorSeverity.LOW,
            received_value=received_value,
            user_message="The subject code already exists.",
            hint="Choose a unique subject code that does not exist in the system."
        )


class SubjectNameAlreadyExistsException(AppBaseException):
    """Raised when a subject name already exists in the system."""
    def __init__(self, received_value: str):
        super().__init__(
            message=f"Subject name '{received_value}' already exists.",
            error_code="SUBJECT_NAME_ALREADY_EXISTS",
            severity=ErrorSeverity.LOW,
            received_value=received_value,
            user_message="The subject name already exists.",
            hint="Choose a unique subject name that does not exist in the system."
        )

class SubjectNotFoundException(AppBaseException):
    """Raised when a subject is not found in the system."""
    def __init__(self, subject_id: ObjectId):
        super().__init__(
            message=f"Subject {subject_id} not found.",
            error_code="SUBJECT_NOT_FOUND",
            status_code=404,
            severity=ErrorSeverity.LOW,
            details={"subject_id": str(subject_id)},
            user_message="The requested subject does not exist.",
            recoverable=True,
            hint="Check the subject ID or create the subject before using it."
        )


class SubjectDeletedException(AppBaseException):
    def __init__(self, subject_id: ObjectId):
        super().__init__(
            message=f"Subject {subject_id} is deleted and cannot be modified.",
            error_code="SUBJECT_DELETED",
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.BUSINESS_LOGIC,
            details={"subject_id": str(subject_id)},
            hint="Restore the subject before modifying it, or create a new one.",
            recoverable=True,
        )




class SubjectPatchFieldNotAllowedException(AppBaseException):
    def __init__(self, field_name: str):
        super().__init__(
            message=f"Field '{field_name}' is not allowed in subject patch update.",
            error_code="SUBJECT_PATCH_FIELD_NOT_ALLOWED",
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.BUSINESS_LOGIC,
            details={"field": field_name},
            user_message="One of the provided fields cannot be updated.",
            hint=f"Remove '{field_name}' from the patch request or use the dedicated endpoint for updating it.",
            recoverable=True,
            status_code=400,
        )



class SubjectNoChangeException(AppBaseException):
    """Raised when a patch/update results in no actual changes."""
    def __init__(self, subject_id: ObjectId):
        super().__init__(
            message=f"Subject {subject_id} update has no changes.",
            error_code="SUBJECT_NO_CHANGE",
            status_code=409,  # conflict: request is valid but does not change state
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.BUSINESS_LOGIC,
            details={"subject_id": str(subject_id)},
            user_message="No changes were detected.",
            hint="Modify at least one field to a different value before saving.",
            recoverable=True,
        )