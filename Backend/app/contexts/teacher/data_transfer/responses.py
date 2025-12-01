from __future__ import annotations
from typing import List
from pydantic import BaseModel
from pydantic.config import ConfigDict

from typing import Optional
from datetime import datetime, date
from app.contexts.school.domain.attendance import AttendanceStatus
from app.contexts.school.domain.grade import GradeType




class TeacherAttendanceDTO(BaseModel):
    id: str
    student_id: str
    student_name: str | None = None 
    class_id: str
    record_date: date
    status: AttendanceStatus
    created_at: datetime
    updated_at: datetime


class TeacherAttendanceListDTO(BaseModel):
    items: List[TeacherAttendanceDTO]

class TeacherGradeDTO(BaseModel):
    id: str
    student_id: str
    student_name: str | None = None   
    class_id: str | None = None
    subject_id: str
    subject_name: str | None = None   # 
    score: float
    type: GradeType
    term: str | None = None
    created_at: datetime
    updated_at: datetime

class TeacherGradeListDTO(BaseModel):
    items: List[TeacherGradeDTO]



class TeacherClassSectionDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    teacher_id: Optional[str]
    student_ids: list[str]
    subject_ids: list[str]
    max_students: Optional[int]
    teacher_name: Optional[str]
    created_at: datetime
    updated_at: datetime

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
