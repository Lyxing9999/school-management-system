from app.contexts.core.error import AppBaseException, ErrorSeverity, ErrorCategory


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