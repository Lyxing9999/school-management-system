from __future__ import annotations

import datetime as dt
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator
from bson import ObjectId

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

def _lifecycle_to_dto(lc) -> LifecycleDTO:
    return LifecycleDTO(
        created_at=lc.created_at,
        updated_at=lc.updated_at,
        deleted_at=lc.deleted_at,
        deleted_by=_oid_to_str(lc.deleted_by),
    )


# ------------ DTOs ------------

class ClassSectionDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    teacher_id: Optional[str]
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
    date: date
    marked_by_teacher_id: Optional[str]
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
        teacher_id=_oid_to_str(section.teacher_id),
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


def attendance_to_dto(record: AttendanceRecord) -> AttendanceDTO:
    return AttendanceDTO(
        id=str(record.id),
        student_id=str(record.student_id),
        class_id=str(record.class_id),
        status=record.status,
        date=record.date,
        marked_by_teacher_id=_oid_to_str(record.marked_by_teacher_id),
        lifecycle=_lifecycle_to_dto(record.lifecycle),
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