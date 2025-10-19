from app.contexts.core.error import AppBaseException, ErrorSeverity, ErrorCategory



class StudentNotFoundException(AppBaseException):
    def __init__(self, student_id: str):
        super().__init__(
            message=f"Student with ID '{student_id}' not found",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message=f"The student ID '{student_id}' is not found.",
            details={"field": "student_id", "value": student_id},
            hint="Ensure the student ID is unique and correctly formatted",
            recoverable=True
        )
    