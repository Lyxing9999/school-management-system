from __future__ import annotations

from datetime import datetime, date as date_type, time
from typing import Any, Dict, Optional

from app.contexts.student.data_transfer.responses import StudentBaseDataDTO
from app.contexts.student.domain.student import Student, Gender, StudentStatus

from app.contexts.student.errors.student_exceptions import (
    StudentMapperRequiredFieldMissingException,
    StudentMapperDobParseException,
    StudentMapperInvalidEnumValueException,
)


class StudentMapper:
    """
    Handles conversion between Student domain model, MongoDB dict, and DTOs.
    """

    REQUIRED_FIELDS = [
        "_id",
        "user_id",
        "student_id_code",
        "first_name_kh",
        "last_name_kh",
        "first_name_en",
        "last_name_en",
        "gender",
        "dob",
        "current_grade_level",
    ]

    @staticmethod
    def _require(data: Dict[str, Any], field: str) -> Any:
        if field not in data:
            raise StudentMapperRequiredFieldMissingException(field=field, available_keys=data.keys())
        return data[field]

    @staticmethod
    def _parse_dob(raw_dob: Any) -> date_type:
        if raw_dob is None:
            raise StudentMapperDobParseException(raw_value=raw_dob, reason="dob is None")

        # stored as datetime in Mongo
        if isinstance(raw_dob, datetime):
            return raw_dob.date()

        # stored as python date
        if isinstance(raw_dob, date_type):
            return raw_dob

        # stored as string
        if isinstance(raw_dob, str):
            try:
                # accepts "YYYY-MM-DD" and full ISO strings
                return datetime.fromisoformat(raw_dob).date()
            except ValueError as e:
                raise StudentMapperDobParseException(raw_value=raw_dob, reason=str(e))

        raise StudentMapperDobParseException(raw_value=raw_dob, reason=f"unsupported type: {type(raw_dob).__name__}")

    @staticmethod
    def _parse_enum(enum_cls, field: str, raw_value: Any, *, strict: bool):
        try:
            return enum_cls(raw_value)
        except Exception:
            if strict:
                allowed = [e.value for e in enum_cls]  # type: ignore
                raise StudentMapperInvalidEnumValueException(field=field, value=raw_value, allowed=allowed)
            # fallback (non-strict)
            return list(enum_cls)[0]

    @staticmethod
    def to_domain(data: Dict[str, Any], *, strict: bool = True) -> Optional[Student]:
        if not data:
            return None

        # Validate required fields (prevents KeyError)
        for f in StudentMapper.REQUIRED_FIELDS:
            StudentMapper._require(data, f)

        dob = StudentMapper._parse_dob(data.get("dob"))

        gender = StudentMapper._parse_enum(Gender, "gender", data.get("gender"), strict=strict)
        status = StudentMapper._parse_enum(StudentStatus, "status", data.get("status", StudentStatus.ACTIVE.value), strict=strict)

        return Student(
            id=data.get("_id"),
            user_id=data.get("user_id"),
            student_id_code=data.get("student_id_code"),
            first_name_kh=data.get("first_name_kh"),
            last_name_kh=data.get("last_name_kh"),
            first_name_en=data.get("first_name_en"),
            last_name_en=data.get("last_name_en"),
            gender=gender,
            dob=dob,
            current_grade_level=data.get("current_grade_level"),
            current_class_id=data.get("current_class_id"),
            photo_url=data.get("photo_url"),
            phone_number=data.get("phone_number"),
            address=data.get("address", {}),
            guardians=data.get("guardians", []),
            status=status,
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),

            history=data.get("history", []),
        )

    @staticmethod
    def to_persistence(student: Student) -> Dict[str, Any]:
        dob_dt = None
        if student.dob:
            dob_dt = datetime.combine(student.dob, time.min)

        return {
            "_id": student.id,
            "user_id": student.user_id,
            "student_id_code": student.student_id_code,
            "first_name_kh": student.first_name_kh,
            "last_name_kh": student.last_name_kh,
            "first_name_en": student.first_name_en,
            "last_name_en": student.last_name_en,
            "gender": student.gender.value,
            "dob": dob_dt,
            "current_grade_level": student.current_grade_level,
            "current_class_id": student.current_class_id,
            "photo_url": student.photo_url,
            "phone_number": student.phone_number,
            "address": student.address,
            "guardians": student.guardians,
            "status": student.status.value,
            "created_at": student.created_at,
            "updated_at": student.updated_at,
            "history": student.history,
        }
    @staticmethod
    def to_dto(student: Student) -> Optional[StudentBaseDataDTO]:
        if not student:
            return None

        return StudentBaseDataDTO(
            id=str(student.id),
            user_id=str(student.user_id),
            student_id_code=student.student_id_code,
            first_name_kh=student.first_name_kh,
            last_name_kh=student.last_name_kh,
            first_name_en=student.first_name_en,
            last_name_en=student.last_name_en,
            gender=student.gender.value if hasattr(student.gender, "value") else str(student.gender),
            dob=student.dob,
            current_grade_level=student.current_grade_level,
            current_class_id=str(student.current_class_id),
            photo_url=student.photo_url,
            phone_number=student.phone_number,
            address=student.address,
            guardians=student.guardians,
            status=student.status.value if hasattr(student.status, "value") else str(student.status),
            created_at=student.created_at,
            updated_at=student.updated_at,
        )