from pydantic import BaseModel, ConfigDict

from app.contexts.iam.data_transfer.response import IAMBaseDataDTO , IAMUpdateDataDTO
from app.contexts.staff.data_transfer.responses import StaffReadDataDTO
from app.contexts.staff.data_transfer.responses import StaffBaseDataDTO
from typing import List, Optional
from app.contexts.school.data_transfer.responses import ClassSectionDTO
from app.contexts.student.data_transfer.responses import StudentBaseDataDTO

import datetime as dt

class BaseNameSelectDTO(BaseModel):
    id: str | None = None
    name: str | None = None
    model_config = {
        "extra": "ignore",
    }

# =====================================================
# SECTION 1: USER MANAGEMENT (IAM)
# =====================================================
class PaginatedUserItemDTO(IAMBaseDataDTO):
    created_by_name: str
    
class PaginatedUsersDataDTO(BaseModel):
    users: List[PaginatedUserItemDTO]
    total: int
    page: int
    page_size: int
    total_pages: int

class AdminCreateUserDataDTO(IAMBaseDataDTO):
    pass

class AdminUpdateUserDataDTO(IAMUpdateDataDTO):
    pass


class AdminDeleteUserDTO(BaseModel):   
    id: str
    model_config = {
        "extra": "allow"
    }

class AdminHardDeleteUserDTO(BaseModel):
    id: str
    deleted: bool
    model_config = {
        "extra": "allow"
    }
# =====================================================
# SECTION 2: STAFF MANAGEMENT
# =====================================================
class AdminGetStaffDataDTO(StaffReadDataDTO):
    pass
class AdminCreateStaffDataDTO(StaffBaseDataDTO):
    pass
class AdminUpdateStaffDataDTO(StaffBaseDataDTO):
    pass
class AdminStaffNameSelectDTO(BaseNameSelectDTO):
    pass


class AdminTeacherSelectDTO(AdminStaffNameSelectDTO):
    staff_name: str

class AdminTeacherSelectListDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: List[AdminTeacherSelectDTO]


class AdminCreateClassDTO(BaseModel):
    model_config = {
        "extra": "allow"
    }
    


# =====================================================
# USER + STAFF
# =====================================================

class AdminUserStaffDataDTO(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",
    )

    user: IAMBaseDataDTO | None = None
    staff: StaffBaseDataDTO | None = None



# =====================================================
# USER + STUDENT
# =====================================================
class AdminCreateStudentDataDTO(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",
    )

    user: IAMBaseDataDTO | None = None
    student: StudentBaseDataDTO | None = None


# =====================================================
# SECTION 3: SUBJECT MANAGEMENT
# =====================================================

class AdminSubjectDataDTO(BaseModel):
    id: str
    name: str
    code: str
    description: Optional[str]
    allowed_grade_levels: List[int]
    is_active: bool
    created_at: dt.datetime
    updated_at: dt.datetime

class AdminSubjectListDTO(BaseModel):
    items: List[AdminSubjectDataDTO]


# =====================================================
# SECTION 4: SCHEDULE MANAGEMENT
# =====================================================
class AdminScheduleSlotDataDTO(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            dt.time: lambda t: t.strftime("%H:%M"),
        },
    )
    id: str
    class_id: str
    teacher_id: str
    day_of_week: int
    start_time: dt.time             
    end_time: dt.time 
    room: str | None = None
    teacher_name: str | None = None
    class_name: str | None = None
    created_at: dt.datetime
    updated_at: dt.datetime


class AdminScheduleListDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: List[AdminScheduleSlotDataDTO]


# =====================================================
# Student Management
# =====================================================

class AdminStudentNameSelectDTO(BaseNameSelectDTO):
    username: str


class AdminStudentNameSelectListDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: List[AdminStudentNameSelectDTO]




# =====================================================
# SECTION 5: CLASS MANAGEMENT
# =====================================================


class AdminClassDataDTO(ClassSectionDTO):
    student_count: int
    subject_count: int
    teacher_id: Optional[str] = None
    teacher_name: str
    subject_labels: List[str] = []






class AdminClassListDTO(BaseModel):
    items: List[AdminClassDataDTO]


class AdminClassSelectDTO(BaseNameSelectDTO):
    pass

class AdminClassSelectListDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: List[AdminClassSelectDTO]




class AdminSubjectNameSelectDTO(BaseNameSelectDTO):
    pass



class AdminSubjectNameSelectListDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: List[AdminSubjectNameSelectDTO]


# =====================================================
# SECTION 6: ADMIN DASHBOARD
# =====================================================

import datetime as dt
from pydantic import BaseModel

class AdminOverviewDTO(BaseModel):
    total_students: int
    total_teachers: int
    total_classes: int
    total_subjects: int
    today_lessons: int


# ----------------- Attendance -----------------

class AdminAttendanceStatusSummaryDTO(BaseModel):
    status: str           # e.g. "present", "absent", "excused"
    count: int


class AdminAttendanceDailyTrendDTO(BaseModel):
    # Aggregation returns date as string or date; Pydantic will parse to dt.date
    date: dt.date
    present: int
    absent: int
    excused: int
    total: int            # we will compute present+absent+excused in read model


class AdminAttendanceByClassDTO(BaseModel):
    class_id: str
    class_name: str
    present: int
    absent: int
    excused: int
    total: int


class AdminTopAbsentStudentDTO(BaseModel):
    student_id: str
    student_name: str
    # These are currently missing in your aggregation, so make them optional
    class_id: str | None = None
    class_name: str | None = None
    absent_count: int
    total_records: int | None = None


class AdminAttendanceDashboardDTO(BaseModel):
    status_summary: list[AdminAttendanceStatusSummaryDTO]
    daily_trend: list[AdminAttendanceDailyTrendDTO]
    by_class: list[AdminAttendanceByClassDTO]
    top_absent_students: list[AdminTopAbsentStudentDTO]


# ----------------- Grades -----------------

class AdminAvgScoreBySubjectDTO(BaseModel):
    subject_id: str
    subject_name: str
    avg_score: float
    sample_size: int


class AdminGradeDistributionBucketDTO(BaseModel):
    range: str   # "0-49", "50-69", ...
    count: int


class AdminPassRateByClassDTO(BaseModel):
    class_id: str
    class_name: str        # we will enrich in read model
    avg_score: float
    pass_rate: float       # 0..1
    total_students: int    # we will map from aggregation field "total"
    passed: int


class AdminGradeDashboardDTO(BaseModel):
    avg_score_by_subject: list[AdminAvgScoreBySubjectDTO]
    grade_distribution: list[AdminGradeDistributionBucketDTO]
    pass_rate_by_class: list[AdminPassRateByClassDTO]


# ----------------- Schedule -----------------

class AdminLessonsByWeekdayDTO(BaseModel):
    day_of_week: int   # 1=Mon..7=Sun
    label: str         # "Mon", "Tue", ...
    lessons: int


class AdminLessonsByTeacherDTO(BaseModel):
    teacher_id: str
    teacher_name: str
    lessons: int
    classes: int


class AdminScheduleDashboardDTO(BaseModel):
    lessons_by_weekday: list[AdminLessonsByWeekdayDTO]
    lessons_by_teacher: list[AdminLessonsByTeacherDTO]


# ----------------- Root Dashboard -----------------

class AdminDashboardDTO(BaseModel):
    overview: AdminOverviewDTO
    attendance: AdminAttendanceDashboardDTO
    grades: AdminGradeDashboardDTO
    schedule: AdminScheduleDashboardDTO