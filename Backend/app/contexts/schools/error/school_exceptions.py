from app.contexts.core.error import AppBaseException, ErrorSeverity, ErrorCategory


#
# SCHOOL CLASS exceptions
#

class ClassNotFoundException(AppBaseException):
    def __init__(self, class_id: str):
        super().__init__(
            message=f"Class with id {class_id} not found",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.DATA,
            status_code=404,
            user_message="Class not found",
            recoverable=False
        )

class DuplicateTeacherException(AppBaseException):
    def __init__(self, teacher_id: str):
        super().__init__(
            message=f"Teacher {teacher_id} already assigned",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.DATA,
            status_code=400,
            user_message="Teacher already assigned",
            recoverable=True
        )



class ClassCreateException(AppBaseException):
    def __init__(self, class_id: str):
        super().__init__(
            message=f"Class creation failed",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            status_code=400,
            user_message="Class creation failed",
            recoverable=True
        )


class ClassUpdateException(AppBaseException):
    def __init__(self, class_id: str, action: str, detail: str | None = None):
        technical_message = (
            f"Class update failed for ID '{class_id}' during action '{action}'."
            + (f" Detail: {detail}" if detail else "")
        )
        user_message = f"Unable to {action} the class. Please try again later."
        super().__init__(
            message=technical_message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            status_code=400,
            user_message=user_message,
            recoverable=True,
        )



class ClassFullException(AppBaseException):
    def __init__(self, max_students: int):
        super().__init__(
            message=f"Class with max students {max_students} is full",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.DATA,
            status_code=400,
            user_message="Class is full",
            recoverable=True
        )



#
# SCHOOL SUBJECT exceptions
#

class SubjectCreateException(AppBaseException):
    def __init__(self, subject_id: str):
        super().__init__(
            message=f"Subject creation failed",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            status_code=400,
            user_message="Subject creation failed",
            recoverable=True
        )
    
class SubjectValueException(AppBaseException):
    def __init__(self, subject_id: str):
        super().__init__(
            message=f"Subject value error",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            status_code=400,
            user_message="Subject value error",
            recoverable=True
        )
    