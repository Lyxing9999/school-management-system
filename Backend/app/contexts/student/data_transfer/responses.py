# app/contexts/student/data_transfer/responses.py
from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

from app.contexts.school.data_transfer.responses import (
    ClassSectionDTO,
    AttendanceDTO,
    GradeDTO,
    
)


class StudentScheduleDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    student_id: str | None = None
    class_id: str | None = None
    subject_id: str | None = None
    day_of_week: int
    start_time: str
    end_time: str
    class_name: Optional[str] = None
    teacher_name: Optional[str] = None
    room: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class StudentClassListDTO(BaseModel):
    items: List[ClassSectionDTO]


class StudentAttendanceListDTO(BaseModel):
    items: List[AttendanceDTO]


class StudentGradeListDTO(BaseModel):
    items: List[GradeDTO]


class StudentScheduleListDTO(BaseModel):
    items: List[StudentScheduleDTO]
    