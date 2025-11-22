from app.contexts.core.error.app_base_exception import (
    AppBaseException,
    ErrorCategory,
    ErrorSeverity
)


class InvalidGradeTypeException(AppBaseException):
    def __init__(self, received_value: str):
        super().__init__(
            message=f"Invalid grade type: {received_value}",
            error_code="GRADE_INVALID_TYPE",
            status_code=400,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.VALIDATION,
            user_message="The grade type provided is not valid.",
            recoverable=True,
            received_value=received_value,
            hint="Valid types: exam, assignment"
        )


class InvalidGradeScoreException(AppBaseException):
    def __init__(self, score: float):
        super().__init__(
            message=f"Invalid grade score: {score}",
            error_code="GRADE_INVALID_SCORE",
            status_code=400,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.VALIDATION,
            user_message="Grade score must be between 0 and 100.",
            recoverable=True,
            received_value=score,
            hint="Provide a score within 0–100 range."
        )


class GradeTypeChangeForbiddenException(AppBaseException):
    def __init__(self, grade_id: str):
        super().__init__(
            message="Cannot change type of a graded record",
            error_code="GRADE_CHANGE_TYPE_FORBIDDEN",
            status_code=409,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="Cannot change the type after a grade is assigned.",
            recoverable=False,
            context={"grade_id": grade_id},
            hint="Once a score is set, the grade type cannot be changed."
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


class NotSubjectTeacherException(AppBaseException):
    def __init__(self, teacher_id: str, subject_id: str, class_id: str | None = None):
        super().__init__(
            message=(
                f"Teacher {teacher_id} is not assigned as subject teacher "
                f"for subject {subject_id}" + (f" in class {class_id}" if class_id else "")
            ),
            error_code="NOT_SUBJECT_TEACHER",
            status_code=403,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="You are not the assigned teacher for this subject.",
            recoverable=False,
            context={
                "teacher_id": teacher_id,
                "subject_id": subject_id,
                "class_id": class_id,
            },
            hint="Only the assigned subject teacher can manage grades for this subject."
        )


class StudentNotEnrolledForSubjectException(AppBaseException):
    def __init__(self, student_id: str, subject_id: str, class_id: str | None = None):
        super().__init__(
            message=(
                f"Student {student_id} is not enrolled in subject {subject_id}"
                + (f" for class {class_id}" if class_id else "")
            ),
            error_code="STUDENT_NOT_ENROLLED_FOR_SUBJECT",
            status_code=409,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="The student is not enrolled in this subject.",
            recoverable=True,
            context={
                "student_id": student_id,
                "subject_id": subject_id,
                "class_id": class_id,
            },
            hint="Enroll the student in the subject before assigning grades."
        )


class GradeNotFoundException(AppBaseException):
    def __init__(self, grade_id: str):
        super().__init__(
            message=f"Grade {grade_id} not found.",
            error_code="GRADE_NOT_FOUND",
            status_code=404,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="The requested grade does not exist.",
            recoverable=True,
            context={"grade_id": grade_id},
            hint="Check the grade ID or create the grade before using it."
        )
