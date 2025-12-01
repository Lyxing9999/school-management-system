from typing import Optional
from app.contexts.core.error import AppBaseException, ErrorSeverity, ErrorCategory
from bson import ObjectId


class NotClassTeacherException(AppBaseException):
    """Raised when a teacher attempts to mark attendance for a class they don't teach."""
    def __init__(self, teacher_id: ObjectId, class_id: ObjectId):
        super().__init__(
            message=f"Teacher {teacher_id} is not assigned to class {class_id}.",
            error_code="ATTENDANCE_NOT_CLASS_TEACHER",
            severity=ErrorSeverity.LOW,
            details={"teacher_id": str(teacher_id), "class_id": str(class_id)},
            hint="Ensure the teacher is assigned to the class before marking attendance."
        )


class StudentNotEnrolledInClassException(AppBaseException):
    """Raised when a student is not enrolled in the class they are being marked for."""
    def __init__(self, student_id: ObjectId, class_id: ObjectId):
        super().__init__(
            message=f"Student {student_id} is not enrolled in class {class_id}.",
            error_code="ATTENDANCE_STUDENT_NOT_ENROLLED",
            severity=ErrorSeverity.LOW,
            details={"student_id": str(student_id), "class_id": str(class_id)},
            hint="Ensure the student is enrolled in the class before marking attendance."
        )


class AttendanceAlreadyMarkedException(AppBaseException):
    """Raised when attendance is already marked for the student on the same date."""
    def __init__(self, student_id: ObjectId, class_id: ObjectId, record_date: Optional[str]):
        super().__init__(
            message=f"Attendance for student {student_id} in class {class_id} on {record_date} is already marked.",
            error_code="ATTENDANCE_ALREADY_MARKED",
            severity=ErrorSeverity.LOW,
            details={"student_id": str(student_id), "class_id": str(class_id), "date": str(record_date)},
            hint="Cannot mark attendance more than once for the same student, class, and date."
        )


class InvalidAttendanceStatusException(AppBaseException):
    """Raised when attendance status is invalid."""
    def __init__(self, received_value):
        super().__init__(
            message=f"Invalid attendance status: {received_value}.",
            error_code="ATTENDANCE_INVALID_STATUS",
            severity=ErrorSeverity.LOW,
            received_value=received_value,
            hint=f"Status must be one of: present, absent, excused."
        )


class AttendanceDateInFutureException(AppBaseException):
    """Raised when the attendance date is in the future."""
    def __init__(self, received_date):
        super().__init__(
            message=f"Attendance date {received_date} cannot be in the future.",
            error_code="ATTENDANCE_DATE_IN_FUTURE",
            severity=ErrorSeverity.LOW,
            received_value=received_date,
            hint="Use the current date or a past date for marking attendance."
        )

class AttendanceNotFoundException(AppBaseException):
    def __init__(self, attendance_id: str):
        super().__init__(
            message=f"Attendance {attendance_id} not found.",
            error_code="ATTENDANCE_NOT_FOUND",
            status_code=404,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="The requested attendance does not exist.",
            recoverable=True,
            context={"attendance_id": attendance_id},
            hint="Check the attendance ID or create the attendance before using it."
        )
    