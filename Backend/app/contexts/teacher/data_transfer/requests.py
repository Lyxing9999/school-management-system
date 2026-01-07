from datetime import date as date_type
from typing import Optional, Any

from pydantic import BaseModel, field_validator

from app.contexts.school.domain.attendance import AttendanceStatus
from app.contexts.school.domain.grade import GradeType


def _empty_to_none(v: Any) -> Any:
    if v is None:
        return None
    if isinstance(v, str) and v.strip() == "":
        return None
    return v




def _parse_enum(enum_cls, v: Any):
    """
    Normalize common bad inputs and raise a clean ValueError
    so Pydantic returns 422 with a useful error.
    """
    if isinstance(v, enum_cls):
        return v
    if isinstance(v, str):
        raw = v.strip().lower()
        try:
            return enum_cls(raw)
        except Exception:
            raise ValueError(f"Invalid {enum_cls.__name__}: {v!r}")
    raise ValueError(f"Invalid {enum_cls.__name__}: {v!r}")


class TeacherMarkAttendanceRequest(BaseModel):
    student_id: str
    class_id: str
    status: AttendanceStatus
    record_date: Optional[date_type] = None

    @field_validator("status", mode="before")
    @classmethod
    def normalize_status(cls, v):
        return _parse_enum(AttendanceStatus, v)

    @field_validator("record_date", mode="before")
    @classmethod
    def normalize_record_date(cls, v):
        return _empty_to_none(v)


class TeacherChangeAttendanceStatusRequest(BaseModel):
    new_status: AttendanceStatus

    @field_validator("new_status", mode="before")
    @classmethod
    def normalize_status(cls, v):
        return _parse_enum(AttendanceStatus, v)


class TeacherAddGradeRequest(BaseModel):
    student_id: str
    subject_id: str
    class_id: Optional[str] = None
    score: float
    type: GradeType
    term: Optional[str] = None

    @field_validator("type", mode="before")
    @classmethod
    def normalize_type(cls, v):
        return _parse_enum(GradeType, v)

    @field_validator("class_id", "term", mode="before")
    @classmethod
    def normalize_optional_strings(cls, v):
        return _empty_to_none(v)


class TeacherUpdateGradeScoreRequest(BaseModel):
    score: float


class TeacherChangeGradeTypeRequest(BaseModel):
    type: GradeType

    @field_validator("type", mode="before")
    @classmethod
    def normalize_type(cls, v):
        return _parse_enum(GradeType, v)