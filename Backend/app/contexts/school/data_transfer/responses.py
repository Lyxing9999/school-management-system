
from typing import Optional, Literal, Any
from pydantic import BaseModel, ConfigDict, field_validator, Field
from bson import ObjectId
import datetime as dt
from datetime import date as date_type
from datetime import datetime
from app.contexts.shared.lifecycle.dto import LifecycleDTO

from app.contexts.school.domain.class_section import ClassSection, ClassSectionStatus
from app.contexts.school.domain.attendance import AttendanceRecord, AttendanceStatus
from app.contexts.school.domain.grade import GradeRecord, GradeType
from app.contexts.school.domain.subject import Subject
from app.contexts.school.domain.schedule import ScheduleSlot


# ------------ Helpers ------------

def _oid_to_str(value: ObjectId | str | None) -> Optional[str]:
    if value is None:
        return None
    return str(value)


def _lifecycle_to_dto(lc: Any) -> LifecycleDTO:
    """
    Accepts: domain Lifecycle object OR dict-like
    """
    if lc is None:
        return LifecycleDTO(created_at=None, updated_at=None, deleted_at=None, deleted_by=None)

    if isinstance(lc, dict):
        return LifecycleDTO(
            created_at=lc.get("created_at"),
            updated_at=lc.get("updated_at"),
            deleted_at=lc.get("deleted_at"),
            deleted_by=_oid_to_str(lc.get("deleted_by")),
        )

    # domain object with attributes
    return LifecycleDTO(
        created_at=getattr(lc, "created_at", None),
        updated_at=getattr(lc, "updated_at", None),
        deleted_at=getattr(lc, "deleted_at", None),
        deleted_by=_oid_to_str(getattr(lc, "deleted_by", None)),
    )

# ------------ DTOs ------------

class ClassSectionDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    homeroom_teacher_id: Optional[str]
    subject_ids: list[str]
    enrolled_count: int
    max_students: int
    status: ClassSectionStatus
    lifecycle: LifecycleDTO


class SubjectDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    code: str
    description: Optional[str] = None
    allowed_grade_levels: list[int]
    is_active: bool
    lifecycle: LifecycleDTO


class AttendanceDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    student_id: str
    class_id: str
    status: AttendanceStatus
    record_date: dt.date

    # who marked it
    marked_by_teacher_id: Optional[str] = None

    # attendance is session-based
    subject_id: str
    schedule_slot_id: str

    lifecycle: LifecycleDTO


class GradeDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    student_id: str
    subject_id: str
    class_id: Optional[str] = None
    teacher_id: Optional[str] = None
    score: float
    type: GradeType
    term: Optional[str] = None
    lifecycle: LifecycleDTO


class ScheduleDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    class_id: str
    teacher_id: str
    subject_id: Optional[str] = None
    day_of_week: int
    start_time: str
    end_time: str
    room: Optional[str] = None
    lifecycle: LifecycleDTO
    
    @field_validator("start_time", "end_time", mode="before")
    @classmethod
    def _time_to_str(cls, v):
        if isinstance(v, dt.time):
            return v.strftime("%H:%M")
        return v


# ------------ Domain -> DTO mappers ------------

def class_section_to_dto(section: ClassSection) -> ClassSectionDTO:
    return ClassSectionDTO(
        id=str(section.id),
        name=section.name,
        homeroom_teacher_id=_oid_to_str(section.homeroom_teacher_id),
        subject_ids=[str(s) for s in section.subject_ids],
        enrolled_count=section.enrolled_count,
        max_students=section.max_students,
        status=section.status,
        lifecycle=_lifecycle_to_dto(section.lifecycle),
    )


def subject_to_dto(subject: Subject) -> SubjectDTO:
    return SubjectDTO(
        id=str(subject.id),
        name=subject.name,
        code=subject.code,
        description=subject.description,
        allowed_grade_levels=list(subject.allowed_grade_levels),
        is_active=subject.is_active,
        lifecycle=_lifecycle_to_dto(subject.lifecycle),
    )



def _to_date(v: Any) -> Optional[dt.date]:
    """
    Normalize various record_date formats to dt.date.
    Accepts: date, datetime, 'YYYY-MM-DD', ISO datetime string, Mongo-style {"$date": ...}
    Returns: dt.date or None
    """
    if v is None:
        return None

    if isinstance(v, date_type) and not isinstance(v, datetime):
        return v

    if isinstance(v, datetime):
        return v.date()

    if isinstance(v, str):
        s = v.strip()
        if not s:
            return None
        # take first 10 chars for YYYY-MM-DD
        try:
            return date_type.fromisoformat(s[:10])
        except Exception:
            return None

    if isinstance(v, dict) and "$date" in v:
        return _to_date(v["$date"])

    try:
        return date_type.fromisoformat(str(v)[:10])
    except Exception:
        return None
# -----------------------------

def attendance_to_dto(record: Any) -> AttendanceDTO:
    def get_field(obj: Any, key: str, default=None):
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    raw_record_date = get_field(record, "record_date", None) or get_field(record, "date", None)
    parsed_date = _to_date(raw_record_date)

    if parsed_date is None:
        # record_date is required by AttendanceDTO, so fail fast with a clear message
        raise ValueError(f"Attendance record_date is missing/invalid: {raw_record_date!r}")

    raw_id = get_field(record, "id", None) or get_field(record, "_id", None)

    return AttendanceDTO(
        id=str(raw_id),
        student_id=str(get_field(record, "student_id")),
        class_id=str(get_field(record, "class_id")),
        status=get_field(record, "status"),
        record_date=parsed_date,  # dt.date

        marked_by_teacher_id=_oid_to_str(
            get_field(record, "marked_by_teacher_id", None) or get_field(record, "teacher_id", None)
        ),

        subject_id=_oid_to_str(get_field(record, "subject_id", None)),
        schedule_slot_id=_oid_to_str(get_field(record, "schedule_slot_id", None)),

        lifecycle=_lifecycle_to_dto(get_field(record, "lifecycle", None)),
    )
def grade_to_dto(grade: GradeRecord) -> GradeDTO:
    return GradeDTO(
        id=str(grade.id),
        student_id=str(grade.student_id),
        subject_id=str(grade.subject_id),
        class_id=_oid_to_str(grade.class_id),
        teacher_id=_oid_to_str(grade.teacher_id),
        score=grade.score,
        type=grade.type,
        term=grade.term,
        lifecycle=_lifecycle_to_dto(grade.lifecycle),
    )


def schedule_to_dto(slot: ScheduleSlot) -> ScheduleDTO:
    return ScheduleDTO(
        id=str(slot.id),
        class_id=str(slot.class_id),
        teacher_id=str(slot.teacher_id),
        subject_id=_oid_to_str(getattr(slot, "subject_id", None)),
        day_of_week=int(slot.day_of_week),
        start_time=slot.start_time.strftime("%H:%M"),
        end_time=slot.end_time.strftime("%H:%M"),
        room=slot.room,
        lifecycle=_lifecycle_to_dto(slot.lifecycle),
    )




class UpdateClassRelationsRequest(BaseModel):
    student_ids: list[str] = Field(default_factory=list)
    homeroom_teacher_id: str | None = None


class ConflictItem(BaseModel):
    student_id: str
    reason: Literal["ALREADY_ENROLLED", "NOT_FOUND"]
    current_class_id: Optional[str] = None


class UpdateClassRelationsResult(BaseModel):
    class_id: str
    homeroom_teacher_changed: bool
    homeroom_teacher_id: str | None
    enrolled_count: int
    added: list[str] = Field(default_factory=list)
    removed: list[str] = Field(default_factory=list)
    conflicts: list[ConflictItem] = Field(default_factory=list)
    capacity_rejected: list[str] = Field(default_factory=list)