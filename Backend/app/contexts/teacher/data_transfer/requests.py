# app/contexts/teacher/data_transfer/requests.py
from __future__ import annotations
from datetime import date
from typing import Optional
from pydantic import BaseModel, field_validator
from app.contexts.school.domain.attendance import AttendanceStatus
from app.contexts.school.domain.grade import GradeType


class TeacherMarkAttendanceRequest(BaseModel):
    student_id: str
    class_id: str
    status: AttendanceStatus | str
    record_date: Optional[date] = None

    @field_validator("status", mode="before")
    def normalize_status(cls, v):
        if isinstance(v, AttendanceStatus):
            return v
        return AttendanceStatus(v)


class TeacherChangeAttendanceStatusRequest(BaseModel):
    new_status: AttendanceStatus | str

    @field_validator("new_status", mode="before")
    def normalize_status(cls, v):
        if isinstance(v, AttendanceStatus):
            return v
        return AttendanceStatus(v)


class TeacherAddGradeRequest(BaseModel):
    student_id: str
    subject_id: str
    class_id: Optional[str] = None
    score: float
    type: GradeType | str
    term: Optional[str] = None

    @field_validator("type", mode="before")
    def normalize_type(cls, v):
        if isinstance(v, GradeType):
            return v
        return GradeType(v)


class TeacherUpdateGradeScoreRequest(BaseModel):
    score: float


class TeacherChangeGradeTypeRequest(BaseModel):
    type: GradeType | str

    @field_validator("type", mode="before")
    def normalize_type(cls, v):
        if isinstance(v, GradeType):
            return v
        return GradeType(v)