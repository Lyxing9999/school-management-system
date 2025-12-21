import datetime as dt
from typing import List, Optional
from pydantic import Field

from .common import BaseDTO


class AdminOverviewDTO(BaseDTO):
    total_students: int
    total_teachers: int
    total_classes: int
    total_subjects: int
    today_lessons: int


# Attendance
class AdminAttendanceStatusSummaryDTO(BaseDTO):
    status: str
    count: int


class AdminAttendanceDailyTrendDTO(BaseDTO):
    date: dt.date
    present: int
    absent: int
    excused: int
    total: int


class AdminAttendanceByClassDTO(BaseDTO):
    class_id: str
    class_name: str
    present: int
    absent: int
    excused: int
    total: int


class AdminTopAbsentStudentDTO(BaseDTO):
    student_id: str
    student_name: str
    class_id: Optional[str] = None
    class_name: Optional[str] = None
    absent_count: int
    total_records: Optional[int] = None


class AdminAttendanceDashboardDTO(BaseDTO):
    status_summary: List[AdminAttendanceStatusSummaryDTO] = Field(default_factory=list)
    daily_trend: List[AdminAttendanceDailyTrendDTO] = Field(default_factory=list)
    by_class: List[AdminAttendanceByClassDTO] = Field(default_factory=list)
    top_absent_students: List[AdminTopAbsentStudentDTO] = Field(default_factory=list)


# Grades
class AdminAvgScoreBySubjectDTO(BaseDTO):
    subject_id: str
    subject_name: str
    avg_score: float
    sample_size: int


class AdminGradeDistributionBucketDTO(BaseDTO):
    range: str
    count: int


class AdminPassRateByClassDTO(BaseDTO):
    class_id: str
    class_name: str
    avg_score: float
    pass_rate: float
    total_students: int
    passed: int


class AdminGradeDashboardDTO(BaseDTO):
    avg_score_by_subject: List[AdminAvgScoreBySubjectDTO] = Field(default_factory=list)
    grade_distribution: List[AdminGradeDistributionBucketDTO] = Field(default_factory=list)
    pass_rate_by_class: List[AdminPassRateByClassDTO] = Field(default_factory=list)


# Schedule Dashboard
class AdminLessonsByWeekdayDTO(BaseDTO):
    day_of_week: int
    label: str
    lessons: int


class AdminLessonsByTeacherDTO(BaseDTO):
    teacher_id: str
    teacher_name: str
    lessons: int
    classes: int


class AdminScheduleDashboardDTO(BaseDTO):
    lessons_by_weekday: List[AdminLessonsByWeekdayDTO] = Field(default_factory=list)
    lessons_by_teacher: List[AdminLessonsByTeacherDTO] = Field(default_factory=list)


class AdminDashboardDTO(BaseDTO):
    overview: AdminOverviewDTO
    attendance: AdminAttendanceDashboardDTO
    grades: AdminGradeDashboardDTO
    schedule: AdminScheduleDashboardDTO