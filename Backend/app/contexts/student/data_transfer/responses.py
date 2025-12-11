# app/contexts/student/data_transfer/responses.py
from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime, date

from app.contexts.school.data_transfer.responses import (
    ClassSectionDTO,

)
from app.contexts.school.data_transfer.responses import GradeType
from app.contexts.school.data_transfer.responses import AttendanceStatus


class StudentBaseDataDTO(BaseModel):
    id: str
    user_id: str
    student_id_code: str
    
    first_name_kh: str
    last_name_kh: str
    first_name_en: str
    last_name_en: str
    
    gender: str
    dob: Optional[date]
    current_grade_level: int
    
    photo_url: Optional[str]
    status: str
    
    created_at: datetime
    updated_at: datetime



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
    items: List[StudentAttendanceDTO]



class StudentGradeDTO(BaseModel):
    id: str
    student_id: str
    student_name: str | None = None
    class_id: str | None = None
    class_name: str | None = None          
    subject_id: str
    subject_label: str | None = None      
    score: float
    type: GradeType
    term: str | None = None
    created_at: datetime
    updated_at: datetime

class StudentGradeListDTO(BaseModel):
    items: List[StudentGradeDTO]


class StudentScheduleListDTO(BaseModel):
    items: List[StudentScheduleDTO]
    


class StudentAttendanceDTO(BaseModel):
    id: str
    student_id: str
    student_name: Optional[str] = None

    class_id: Optional[str] = None
    class_name: Optional[str] = None

    status: AttendanceStatus
    record_date: date

    marked_by_teacher_id: str
    teacher_name: Optional[str] = None

    created_at: datetime
    updated_at: datetime

class StudentAttendanceListDTO(BaseModel):
    items: List[StudentAttendanceDTO]
