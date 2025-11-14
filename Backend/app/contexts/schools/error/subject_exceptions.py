from app.contexts.core.error import AppBaseException, ErrorSeverity, ErrorCategory

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
    