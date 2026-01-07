from datetime import date as date_type
from typing import Optional, Any, Dict, Iterable

from app.contexts.core.errors.app_base_exception import (
    AppBaseException,
    ErrorSeverity,
    ErrorCategory,
)

from bson import ObjectId

class StudentDobTypeInvalidException(AppBaseException):
    def __init__(self, received_type: str, received_value: Any = None):
        super().__init__(
            message=f"Invalid DOB type. Expected date, got '{received_type}'.",
            error_code="STUDENT_DOB_TYPE_INVALID",
            status_code=400,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="Date of birth format is invalid.",
            recoverable=True,
            context={
                "expected_type": "date",
                "received_type": received_type,
                "received_value": str(received_value),
            },
            hint="Pass DOB as a Python date object (convert from string in DTO/service layer).",
        )


class StudentDobInFutureException(AppBaseException):
    def __init__(self, dob: date_type, today: date_type):
        super().__init__(
            message=f"Invalid DOB. '{dob.isoformat()}' is in the future (today={today.isoformat()}).",
            error_code="STUDENT_DOB_IN_FUTURE",
            status_code=400,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="Date of birth cannot be in the future.",
            recoverable=True,
            context={"dob": dob.isoformat(), "today": today.isoformat()},
            hint="Choose a valid birth date (must be today or earlier).",
        )


class StudentAgeOutOfRangeException(AppBaseException):
    def __init__(self, dob: date_type, age: int, min_age: int, max_age: int, today: date_type):
        super().__init__(
            message=(
                f"Student age out of range. dob={dob.isoformat()}, age={age}, "
                f"allowed_range={min_age}-{max_age}, today={today.isoformat()}."
            ),
            error_code="STUDENT_AGE_OUT_OF_RANGE",
            status_code=400,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message=f"Student age must be between {min_age} and {max_age} years.",
            recoverable=True,
            context={
                "dob": dob.isoformat(),
                "age": age,
                "min_age": min_age,
                "max_age": max_age,
                "today": today.isoformat(),
            },
            hint=f"Use a DOB that results in age between {min_age} and {max_age} (inclusive).",
        )


class StudentDobStringFormatInvalidException(AppBaseException):
    def __init__(self, value: str, expected_format: str = "%Y-%m-%d"):
        super().__init__(
            message=f"Invalid DOB string format. value='{value}', expected_format='{expected_format}'.",
            error_code="STUDENT_DOB_STRING_FORMAT_INVALID",
            status_code=400,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="Date of birth format is invalid. Use YYYY-MM-DD.",
            recoverable=True,
            context={"dob": value, "expected_format": expected_format},
            hint="Example: 2010-05-12",
        )






class StudentCannotJoinClassWhenNotActiveException(AppBaseException):
    def __init__(
        self,
        *,
        student_id: Optional[ObjectId] = None,
        class_id: Optional[ObjectId] = None,
        status: Any = None,
    ):
        super().__init__(
            message=(
                "Student cannot join class because student is not ACTIVE. "
                f"student_id={student_id}, class_id={class_id}, status={status}."
            ),
            error_code="STUDENT_CANNOT_JOIN_CLASS_NOT_ACTIVE",
            status_code=403,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="Only active students can join a class.",
            recoverable=True,
            context={
                "student_id": str(student_id) if student_id is not None else None,
                "class_id": str(class_id) if class_id is not None else None,
                "status": str(status),
                "required_status": "ACTIVE",
            },
            hint="Activate the student account (or restore from suspension) before joining a class.",
        )




class StudentUserNotFoundException(AppBaseException):
    def __init__(self, user_id: Any):
        super().__init__(
            message=f"User not found. user_id={user_id}.",
            error_code="STUDENT_USER_NOT_FOUND",
            status_code=404,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="User not found.",
            recoverable=True,
            context={"user_id": str(user_id)},
            hint="Verify the user_id exists before creating a student profile.",
        )

    
class StudentNotFoundException(AppBaseException):
    def __init__(self, student_id: Any):
        super().__init__(
            message=f"Student not found. student_id={student_id}.",
            error_code="STUDENT_NOT_FOUND",
            status_code=404,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="Student not found.",
            recoverable=True,
            context={"student_id": str(student_id)},
            hint="Verify the student_id exists in a student profile.",
        )


class StudentProfileAlreadyExistsException(AppBaseException):
    def __init__(self, user_id: Any, existing_student_id: Optional[ObjectId] = None):
        super().__init__(
            message=f"Student profile already exists for user. user_id={user_id}, existing_student_id={existing_student_id}.",
            error_code="STUDENT_PROFILE_ALREADY_EXISTS",
            status_code=409,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="This user already has a student profile.",
            recoverable=True,
            context={
                "user_id": str(user_id),
                "existing_student_id": str(existing_student_id) if existing_student_id else None,
            },
            hint="Use the existing student profile or delete/archive it before creating a new one.",
        )


class StudentCodeAlreadyExistsException(AppBaseException):
    def __init__(self, student_id_code: str):
        super().__init__(
            message=f"Student code already exists. student_id_code='{student_id_code}'.",
            error_code="STUDENT_CODE_ALREADY_EXISTS",
            status_code=409,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="Student ID code already exists.",
            recoverable=True,
            context={"student_id_code": student_id_code},
            hint="Generate a new unique student_id_code.",
        )


class StudentInvalidObjectIdException(AppBaseException):
    """
    Optional: use when user_id / created_by is not a valid ObjectId.
    """
    def __init__(self, field: str, value: Any):
        super().__init__(
            message=f"Invalid ObjectId for field '{field}'. value={value}.",
            error_code="STUDENT_INVALID_OBJECT_ID",
            status_code=400,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="Invalid identifier format.",
            recoverable=True,
            context={"field": field, "value": str(value)},
            hint="Provide a valid MongoDB ObjectId string.",
        )





class StudentMapperRequiredFieldMissingException(AppBaseException):
    def __init__(self, field: str, available_keys: Iterable[str]):
        super().__init__(
            message=f"StudentMapper missing required field '{field}'. available_keys={list(available_keys)}",
            error_code="STUDENT_MAPPER_REQUIRED_FIELD_MISSING",
            status_code=500,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="Student data is corrupted or incomplete.",
            recoverable=False,
            context={"missing_field": field, "available_keys": list(available_keys)},
            hint="Ensure Mongo document contains all required fields before mapping to domain.",
        )


class StudentMapperDobParseException(AppBaseException):
    def __init__(self, raw_value: Any, reason: str = ""):
        super().__init__(
            message=f"StudentMapper failed to parse dob. raw_value={raw_value}, reason={reason}",
            error_code="STUDENT_MAPPER_DOB_PARSE_FAILED",
            status_code=500,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="Student DOB is invalid in storage.",
            recoverable=False,
            context={"raw_dob": str(raw_value), "reason": reason},
            hint="Persist DOB as datetime or ISO date string (YYYY-MM-DD / ISO8601).",
        )


class StudentMapperInvalidEnumValueException(AppBaseException):
    def __init__(self, field: str, value: Any, allowed: list[str]):
        super().__init__(
            message=f"StudentMapper invalid enum value for {field}. value={value}, allowed={allowed}",
            error_code="STUDENT_MAPPER_INVALID_ENUM_VALUE",
            status_code=500,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="Student data contains invalid enum value.",
            recoverable=False,
            context={"field": field, "value": str(value), "allowed": allowed},
            hint="Fix invalid stored value or migrate data to valid enum values.",
        )


class StudentNotFoundException(AppBaseException):
    def __init__(
        self,
        *,
        student_id: Optional[ObjectId] = None,
        user_id: Any = None,
        lookup_field: str = "student_id",
    ):
        super().__init__(
            message=(
                "Student not found. "
                f"lookup_field={lookup_field}, student_id={student_id}, user_id={user_id}."
            ),
            error_code="STUDENT_NOT_FOUND",
            status_code=404,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="Student not found.",
            recoverable=True,
            context={
                "lookup_field": lookup_field,
                "student_id": str(student_id) if student_id is not None else None,
                "user_id": str(user_id) if user_id is not None else None,
            },
            hint="Verify the student exists (correct student_id/user_id) and is not archived/deleted.",
        )

class StudentUpdateFailedException(AppBaseException):
    def __init__(self, *, user_id: Any = None, student_id: Optional[ObjectId] = None, reason: str = ""):
        super().__init__(
            message=f"Student update failed. user_id={user_id}, student_id={student_id}, reason={reason}",
            error_code="STUDENT_UPDATE_FAILED",
            status_code=500,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.DATABASE,
            user_message="Failed to update student profile.",
            recoverable=False,
            context={
                "user_id": str(user_id) if user_id is not None else None,
                "student_id": str(student_id) if student_id is not None else None,
                "reason": reason,
            },
            hint="Check database write operation and ensure the student record exists.",
        )