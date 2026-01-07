from typing import List, Optional
from datetime import date
from pydantic import BaseModel
from pydantic.config import ConfigDict

from app.contexts.school.domain.attendance import AttendanceStatus
from app.contexts.school.domain.grade import GradeType
from app.contexts.school.data_transfer.responses import ClassSectionDTO
from app.contexts.shared.lifecycle.dto import LifecycleDTO
from app.contexts.student.data_transfer.responses import StudentBaseDataDTO


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

    lifecycle: LifecycleDTO


class TeacherAttendanceListDTO(BaseModel):
    items: List[TeacherAttendanceDTO]


class TeacherGradeDTO(BaseModel):
    id: str
    student_id: str
    class_id: str
    subject_id: str
    teacher_id: str
    score: float
    type: GradeType
    term: Optional[str] = None
    lifecycle: LifecycleDTO

    # enriched fields
    student_name: Optional[str] = None
    student_name_en: Optional[str] = None
    student_name_kh: Optional[str] = None

    class_name: Optional[str] = None
    teacher_name: Optional[str] = None
    subject_label: Optional[str] = None


class TeacherGradePagedListDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: List[TeacherGradeDTO]
    total: int
    page: int
    page_size: int
    pages: int


class TeacherClassSectionDTO(ClassSectionDTO):
    enrolled_count: int
    subject_count: int

    teacher_id: Optional[str] = None
    homeroom_teacher_name: Optional[str] = None

    subject_labels: List[str] = []
    assigned_subject_labels: List[str] = []   
    is_homeroom: Optional[bool] = None        

    lifecycle: LifecycleDTO

class TeacherClassSectionListDTO(BaseModel):
    items: List[TeacherClassSectionDTO]


class TeacherStudentDTO(StudentBaseDataDTO):
    pass


class TeacherStudentListDTO(BaseModel):
    items: List[TeacherStudentDTO]


class TeacherStudentNameSelectDTO(BaseModel):
    value: str
    label: str | None = None
    first_name_kh: Optional[str] = None
    last_name_kh: Optional[str] = None
    first_name_en: Optional[str] = None
    last_name_en: Optional[str] = None
    full_name_kh: Optional[str] = None
    full_name_en: Optional[str] = None
    model_config = {"extra": "ignore"}


class TeacherStudentSelectNameListDTO(BaseModel):
    items: List[TeacherStudentNameSelectDTO]


class TeacherSubjectNameSelectDTO(BaseModel):
    value: str
    label: str | None = None
    model_config = {"extra": "ignore"}


class TeacherSubjectSelectNameListDTO(BaseModel):
    items: List[TeacherSubjectNameSelectDTO]


class TeacherClassNameSelectDTO(BaseModel):
    value: str
    label: str | None = None
    model_config = {"extra": "ignore"}


class TeacherClassNameSelectListDTO(BaseModel):
    items: List[TeacherClassNameSelectDTO]


class TeacherScheduleDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    class_id: str
    teacher_id: str

    subject_id: Optional[str] = None

    day_of_week: int
    start_time: str
    end_time: str

    class_name: Optional[str] = None
    teacher_name: Optional[str] = None
    subject_label: Optional[str] = None
    room: Optional[str] = None

    lifecycle: LifecycleDTO


class TeacherScheduleListDTO(BaseModel):
    items: List[TeacherScheduleDTO]
    total: int
    page: int
    page_size: int
    pages: int


class TeacherClassSummaryDTO(BaseModel):
    total_classes: int
    total_students: int
    total_subjects: int


class TeacherClassSectionSummaryDTO(BaseModel):
    items: List[TeacherClassSectionDTO]
    summary: TeacherClassSummaryDTO


class TeacherAssignmentDTO(BaseModel):
    id: str
    class_id: str
    subject_id: str
    teacher_id: str
    assigned_by: Optional[str] = None
    lifecycle: LifecycleDTO

    # enrichment
    class_name: Optional[str] = None
    subject_label: Optional[str] = None
    teacher_name: Optional[str] = None
    assigned_by_username: Optional[str] = None

class TeacherAssignmentListDTO(BaseModel):
    items: List[TeacherAssignmentDTO]