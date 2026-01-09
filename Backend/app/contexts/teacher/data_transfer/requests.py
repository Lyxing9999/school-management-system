import re
import datetime as dt
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
    if isinstance(v, enum_cls):
        return v
    if isinstance(v, str):
        raw = v.strip().lower()
        try:
            return enum_cls(raw)
        except Exception:
            raise ValueError(f"Invalid {enum_cls.__name__}: {v!r}")
    raise ValueError(f"Invalid {enum_cls.__name__}: {v!r}")

# Accept: "S1" / "S2"
TERM_SHORT_RE = re.compile(r"^(S1|S2)$", re.IGNORECASE)

# Accept: "2025-S1" / "2025-S2"
TERM_FULL_RE = re.compile(r"^(?P<year>\d{4})-(?P<sem>S1|S2)$", re.IGNORECASE)

def current_school_year() -> int:
    # simplest rule: calendar year
    return dt.datetime.utcnow().year
class TeacherMarkAttendanceRequest(BaseModel):
    student_id: str
    class_id: str
    subject_id: str
    schedule_slot_id: str
    status: AttendanceStatus
    record_date: Optional[dt.date] = None

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
    class_id: str | None = None
    score: float
    type: Any  # keep your GradeType here
    term: str  # REQUIRED

    @field_validator("term", mode="before")
    @classmethod
    def normalize_term(cls, v):
        if v is None:
            raise ValueError("term is required")
        if not isinstance(v, str):
            raise ValueError("term must be a string")

        t = v.strip().upper()
        if not t:
            raise ValueError("term cannot be empty")

        # Case 1: "S1" or "S2" -> attach year
        if TERM_SHORT_RE.match(t):
            y = current_school_year()
            return f"{y}-{t}"

        # Case 2: "YYYY-S1"/"YYYY-S2" -> validate year range
        m = TERM_FULL_RE.match(t)
        if not m:
            raise ValueError("term format must be S1/S2 or YYYY-S1/YYYY-S2 (e.g. S1 or 2025-S1)")

        year = int(m.group("year"))
        if year < 2000 or year > 2100:
            raise ValueError("term year must be between 2000 and 2100")

        return f"{year}-{m.group('sem').upper()}"

    @field_validator("score")
    @classmethod
    def validate_score(cls, v):
        if v < 0 or v > 100:
            raise ValueError("score must be between 0 and 100")
        return v

class TeacherUpdateGradeScoreRequest(BaseModel):
    score: float

    @field_validator("score")
    @classmethod
    def validate_score(cls, v):
        if v < 0 or v > 100:
            raise ValueError("score must be between 0 and 100")
        return v


class TeacherChangeGradeTypeRequest(BaseModel):
    type: GradeType

    @field_validator("type", mode="before")
    @classmethod
    def normalize_type(cls, v):
        return _parse_enum(GradeType, v)