from __future__ import annotations
from typing import List
from pydantic import BaseModel
from pydantic.config import ConfigDict

from typing import Optional
from datetime import datetime, date
from app.contexts.school.domain.attendance import AttendanceStatus
from app.contexts.school.domain.grade import GradeType
from app.contexts.school.data_transfer.responses import ClassSectionDTO





class TeacherAttendanceDTO(BaseModel):
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

class TeacherAttendanceListDTO(BaseModel):
    items: List[TeacherAttendanceDTO]

class TeacherGradeDTO(BaseModel):
    id: str
    student_id: str
    student_name: Optional[str] = None
    class_id: Optional[str] = None
    class_name: Optional[str] = None
    subject_id: str
    subject_label: Optional[str] = None  
    teacher_id: Optional[str] = None
    teacher_name: Optional[str] = None
    score: float
    type: GradeType
    term: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class TeacherGradeListDTO(BaseModel):
    items: List[TeacherGradeDTO]



class TeacherClassSectionDTO(ClassSectionDTO):
    student_count: int
    subject_count: int
    teacher_id: Optional[str] = None
    teacher_name: str
    subject_labels: List[str] = []


class TeacherClassSectionListDTO(BaseModel):
    items: List[TeacherClassSectionDTO]

# student name
class TeacherStudentNameSelectDTO(BaseModel):
    id: str
    username: str  # TODO: later switch to real student full_name
    model_config = {"extra": "ignore"}


class TeacherStudentSelectNameListDTO(BaseModel):
    items: List[TeacherStudentNameSelectDTO]

# subject name
class TeacherSubjectNameSelectDTO(BaseModel):
    id: str
    name: str
    model_config = {"extra": "ignore"}


class TeacherSubjectSelectNameListDTO(BaseModel):
    items: List[TeacherSubjectNameSelectDTO]


class TeacherClassNameSelectDTO(BaseModel):
    id: str
    name: str
    model_config = {"extra": "ignore"}


class TeacherClassNameSelectListDTO(BaseModel):
    items: List[TeacherClassNameSelectDTO]



class TeacherScheduleDTO(BaseModel):
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


class TeacherScheduleListDTO(BaseModel):
    items: List[TeacherScheduleDTO]




class TeacherClassSummaryDTO(BaseModel):
    total_classes: int
    total_students: int
    total_subjects: int


class TeacherClassSectionSummaryDTO(BaseModel):
    items: List[TeacherClassSectionDTO]
    summary: TeacherClassSummaryDTO