# app/contexts/school/errors/class_section_errors.py
from __future__ import annotations

from typing import Any, Dict, Optional
from bson import ObjectId

from app.contexts.core.error.app_base_exception import (
    AppBaseException,
    ErrorSeverity,
    ErrorCategory,
)


# -------------------------
# Basic Validation Errors
# -------------------------

class InvalidClassSectionNameError(AppBaseException):
    """Raised when the class section name is empty or invalid."""
    def __init__(self, received_value: Any):
        super().__init__(
            message="ClassSection name cannot be empty or whitespace.",
            error_code="CLASSSECTION_INVALID_NAME",
            status_code=400,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.VALIDATION,
            user_message="Class name is invalid.",
            recoverable=True,
            context={"received_value": str(received_value)},
            hint="Provide a non-empty string for the class name.",
        )


class InvalidMaxStudentsError(AppBaseException):
    """Raised when max_students is <= 0."""
    def __init__(self, received_value: Any):
        super().__init__(
            message=f"Invalid max_students. Expected positive integer or None, got {received_value}.",
            error_code="CLASSSECTION_INVALID_MAX_STUDENTS",
            status_code=400,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.VALIDATION,
            user_message="Maximum students must be a positive number.",
            recoverable=True,
            context={"received_value": received_value},
            hint="Assign a positive integer (e.g. 30) or None to disable capacity limit.",
        )


class InvalidSubjectIdError(AppBaseException):
    """Raised when subject_id is not a valid ObjectId."""
    def __init__(self, received_value: Any):
        super().__init__(
            message=f"Subject ID is not a valid ObjectId: {received_value}",
            error_code="CLASSSECTION_INVALID_SUBJECT_ID",
            status_code=400,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.VALIDATION,
            user_message="Invalid subject ID.",
            recoverable=True,
            context={"received_value": str(received_value)},
            hint="Provide a valid MongoDB ObjectId for subject_id.",
        )


class InvalidTeacherIdError(AppBaseException):
    """Raised when teacher_id is not a valid ObjectId."""
    def __init__(self, received_value: Any):
        super().__init__(
            message=f"Teacher ID is not a valid ObjectId: {received_value}",
            error_code="CLASSSECTION_INVALID_TEACHER_ID",
            status_code=400,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.VALIDATION,
            user_message="Invalid teacher ID.",
            recoverable=True,
            context={"received_value": str(received_value)},
            hint="Provide a valid MongoDB ObjectId for teacher_id.",
        )


# -------------------------
# Capacity / Enrollment Errors
# -------------------------

class StudentCapacityExceededError(AppBaseException):
    """Raised when current enrollment exceeds max capacity (invariant violated)."""
    def __init__(self, class_name: str, max_students: int, current_count: int):
        super().__init__(
            message=(
                f"ClassSection '{class_name}' exceeds max capacity. "
                f"max_students={max_students}, current_count={current_count}."
            ),
            error_code="CLASSSECTION_CAPACITY_EXCEEDED",
            status_code=409,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="Class capacity exceeded.",
            recoverable=True,
            context={
                "class_name": class_name,
                "max_students": max_students,
                "current_count": current_count,
            },
            hint="Increase max_students or remove a student to reduce enrollment.",
        )


class ClassSectionFullException(AppBaseException):
    """Raised when trying to enroll but the class is already full."""
    def __init__(
        self,
        *,
        class_id: Optional[ObjectId] = None,
        max_students: Optional[int] = None,
        current_count: Optional[int] = None,
    ):
        super().__init__(
            message=(
                "Cannot enroll student: class is full. "
                f"class_id={class_id}, max_students={max_students}, current_count={current_count}."
            ),
            error_code="CLASSSECTION_FULL",
            status_code=409,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="This class is full. Please choose another class.",
            recoverable=True,
            context={
                "class_id": str(class_id) if class_id else None,
                "max_students": max_students,
                "current_count": current_count,
            },
            hint="Enroll the student in a different class or increase max_students.",
        )


class StudentAlreadyEnrolledException(AppBaseException):
    """
    Raised when trying to enroll a student who is already assigned to a different class.
    """
    def __init__(self, student_id: ObjectId, current_class_id: ObjectId, target_class_id: ObjectId):
        super().__init__(
            message=f"Student {student_id} cannot join class {target_class_id} because they are already enrolled in class {current_class_id}.",
            error_code="STUDENT_ALREADY_HAS_CLASS",
            status_code=409,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="This student is already enrolled in another class. Please unenroll them first.",
            recoverable=True,
            context={"student_id": str(student_id), "current_class_id": str(current_class_id), "target_class_id": str(target_class_id)},
            hint="Unenroll the student from their current class before enrolling them in a new one.",
        )


# -------------------------
# Uniqueness / Constraints
# -------------------------

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
            hint="Class names must be unique.",
        )


class TeacherOverClassLoadException(AppBaseException):
    def __init__(self, teacher_id: ObjectId | str, max_load: int):
        super().__init__(
            message=f"Teacher {teacher_id} has reached maximum class load of {max_load}.",
            error_code="TEACHER_OVER_CLASS_LOAD",
            status_code=409,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="This teacher is assigned to the maximum allowed number of classes.",
            recoverable=True,
            context={"teacher_id": str(teacher_id), "max_load": max_load},
            hint="Assign a different teacher or increase the allowed max class load.",
        )


# -------------------------
# Not Found Errors
# -------------------------

class ClassNotFoundException(AppBaseException):
    def __init__(self, class_id: ObjectId):
        super().__init__(
            message=f"Class {class_id} not found.",
            error_code="CLASS_NOT_FOUND",
            status_code=404,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="The requested class does not exist.",
            recoverable=True,
            context={"class_id": str(class_id)},
            hint="Check the class ID and try again.",
        )