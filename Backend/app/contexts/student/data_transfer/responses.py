# app/contexts/student/data_transfer/responses.py
from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

from app.contexts.school.data_transfer.responses import (
    ClassSectionDTO,
    AttendanceDTO,

    
)
class StudentClassSectionDTO(ClassSectionDTO):
    student_count: int
    subject_count: int
    teacher_id: Optional[str] = None
    teacher_name: str
    subject_labels: List[str] = []


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
    items: List[StudentClassSectionDTO]


class StudentAttendanceListDTO(BaseModel):
    items: List[AttendanceDTO]



class StudentGradeDTO(BaseModel):
    id: str
    student_id: str
    student_name: str | None = None
    class_id: str | None = None
    class_name: str | None = None           # add this if you want it
    subject_id: str
    subject_label: str | None = None        # or subject_name if you prefer
    score: float
    type: GradeType
    term: str | None = None
    created_at: datetime
    updated_at: datetime

class StudentGradeListDTO(BaseModel):
    items: List[StudentGradeDTO]


class StudentScheduleListDTO(BaseModel):
    items: List[StudentScheduleDTO]
    