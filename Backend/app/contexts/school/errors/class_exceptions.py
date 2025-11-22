# app/contexts/school/domain/class_section_errors.py
from app.contexts.core.error import AppBaseException, ErrorSeverity, ErrorCategory 
from bson import ObjectId


class ClassSectionError(AppBaseException):
    """Base class for all ClassSection domain errors."""
    def __init__(self, message: str, **kwargs):
        severity = kwargs.pop("severity", ErrorSeverity.MEDIUM)
        super().__init__(
            message=message,
            category=ErrorCategory.BUSINESS_LOGIC,
            severity=severity,
            **kwargs
        )


class InvalidClassSectionNameError(ClassSectionError):
    """Raised when the class section name is empty or invalid."""
    def __init__(self, received_value: str):
        super().__init__(
            message="ClassSection name cannot be empty.",
            error_code="CLASSSECTION_INVALID_NAME",
            severity=ErrorSeverity.LOW,
            received_value=received_value,
            hint="Provide a non-empty string for the class name."
        )


class StudentCapacityExceededError(ClassSectionError):
    """Raised when adding a student exceeds max capacity."""
    def __init__(self, class_name: str, max_students: int, current_count: int):
        super().__init__(
            message=f"ClassSection '{class_name}' exceeds max capacity ({max_students}).",
            error_code="CLASSSECTION_CAPACITY_EXCEEDED",
            severity=ErrorSeverity.MEDIUM,
            details={
                "max_students": max_students,
                "current_student_count": current_count
            },
            hint="Increase max_students or remove a student first."
        )


class InvalidMaxStudentsError(ClassSectionError):
    """Raised when max_students is <= 0."""
    def __init__(self, received_value: int):
        super().__init__(
            message="max_students must be a positive integer.",
            error_code="CLASSSECTION_INVALID_MAX_STUDENTS",
            severity=ErrorSeverity.LOW,
            received_value=received_value,
            hint="Assign a positive integer or None."
        )


class DuplicateStudentEnrollmentError(ClassSectionError):
    """Raised when a student is already enrolled."""
    def __init__(self, student_id: ObjectId, class_id: ObjectId):
        super().__init__(
            message=f"Student {student_id} is already enrolled in class {class_id}.",
            error_code="CLASSSECTION_DUPLICATE_ENROLLMENT",
            severity=ErrorSeverity.LOW,
            details={"student_id": str(student_id), "class_id": str(class_id)},
        )


class InvalidSubjectIdError(ClassSectionError):
    """Raised when subject_id is not a valid ObjectId."""
    def __init__(self, received_value):
        super().__init__(
            message="Subject ID is not a valid ObjectId.",
            error_code="CLASSSECTION_INVALID_SUBJECT_ID",
            severity=ErrorSeverity.LOW,
            received_value=received_value
        )


class InvalidTeacherIdError(ClassSectionError):
    """Raised when teacher_id is not a valid ObjectId."""
    def __init__(self, received_value):
        super().__init__(
            message="Teacher ID is not a valid ObjectId.",
            error_code="CLASSSECTION_INVALID_TEACHER_ID",
            severity=ErrorSeverity.LOW,
            received_value=received_value
        )
class ClassNameAlreadyExistsException(AppBaseException):
    def __init__(self, name: str):
        super().__init__(
            message=f"Class with name '{name}' already exists.",
            error_code="CLASS_NAME_ALREADY_EXISTS",
            status_code=409,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="The class name is already used. Choose another one.",
            recoverable=True,
            context={"class_name": name},
            hint="Class names must be unique."
        )


class TeacherOverClassLoadException(AppBaseException):
    def __init__(self, teacher_id: str, max_load: int):
        super().__init__(
            message=f"Teacher {teacher_id} has reached maximum class load of {max_load}.",
            error_code="TEACHER_OVER_CLASS_LOAD",
            status_code=409,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="This teacher is assigned to the maximum allowed number of classes.",
            recoverable=False,
            context={"teacher_id": teacher_id, "max_load": max_load},
            hint="Assign a different teacher or increase max class load if allowed."
        )


class ClassNotFoundException(AppBaseException):
    def __init__(self, class_id: ObjectId):
        super().__init__(
            message=f"Class {class_id} not found.",
            error_code="CLASS_NOT_FOUND",
            status_code=404,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.BUSINESS_LOGIC,
            details={"class_id": str(class_id)},
            user_message="The requested class does not exist.",
            recoverable=True,
        )