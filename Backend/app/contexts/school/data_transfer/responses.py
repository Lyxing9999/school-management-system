# app/contexts/school/data_transfer/responses.py
from __future__ import annotations
from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from bson import ObjectId

from app.contexts.school.domain.class_section import ClassSection
from app.contexts.school.domain.attendance import AttendanceRecord, AttendanceStatus
from app.contexts.school.domain.grade import GradeRecord, GradeType
from app.contexts.school.domain.subject import Subject


# ------------ Base DTOs ------------

class ClassSectionDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    teacher_id: Optional[str]
    student_ids: list[str]
    subject_ids: list[str]
    max_students: Optional[int]
    created_at: datetime
    updated_at: datetime

class SubjectDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    code: str
    description: Optional[str] = None
    allowed_grade_levels: list[int]
    is_active: bool
    created_at: datetime
    updated_at: datetime


class AttendanceDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    student_id: str
    class_id: str
    status: AttendanceStatus
    date: date
    marked_by_teacher_id: Optional[str]
    created_at: datetime
    updated_at: datetime


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
    created_at: datetime
    updated_at: datetime



class ScheduleDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    student_id: str
    class_id: str
    subject_id: str
    day_of_week: int
    start_time: str
    end_time: str
    room: Optional[str] = None
    created_at: datetime
    updated_at: datetime



# ------------ Mapping helpers ------------

def _oid_to_str(value) -> Optional[str]:
    if isinstance(value, ObjectId):
        return str(value)
    if value is None:
        return None
    return str(value)


def class_section_to_dto(section: ClassSection) -> ClassSectionDTO:
    return ClassSectionDTO(
        id=str(section.id),
        name=section.name,
        teacher_id=_oid_to_str(section.teacher_id),
        student_ids=[_oid_to_str(s) for s in section.student_ids],
        subject_ids=[_oid_to_str(s) for s in section.subject_ids],
        max_students=section.max_students,
        created_at=section.created_at,
        updated_at=section.updated_at,
    )


def subject_to_dto(subject: Subject) -> SubjectDTO:
    return SubjectDTO(
        id=str(subject.id),
        name=subject.name,
        code=subject.code,
        description=subject.description,
        allowed_grade_levels=list(subject.allowed_grade_levels),
        is_active=subject.is_active,
        created_at=subject.created_at,
        updated_at=subject.updated_at,
    )


def attendance_to_dto(record: AttendanceRecord) -> AttendanceDTO:
    return AttendanceDTO(
        id=str(record.id),
        student_id=str(record.student_id),
        class_id=str(record.class_id),
        status=record.status,
        date=record.date,
        marked_by_teacher_id=_oid_to_str(record.marked_by_teacher_id),
        created_at=record.created_at,
        updated_at=record.updated_at,
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
        created_at=grade.created_at,
        updated_at=grade.updated_at,
    )


def schedule_to_dto(schedule: dict) -> ScheduleDTO:
    return ScheduleDTO(
        id=str(schedule["_id"]),
        student_id=str(schedule["student_id"]),
        class_id=str(schedule["class_id"]),
        subject_id=str(schedule["subject_id"]),
        day_of_week=schedule["day_of_week"],
        start_time=schedule["start_time"],
        end_time=schedule["end_time"],
        room=schedule.get("room"),
        created_at=schedule["created_at"],
        updated_at=schedule["updated_at"],
    )


