import datetime as dt
from typing import List, Optional, Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class BaseDTO(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",
        use_enum_values=True,
    )


# -----------------------------
# Overview
# -----------------------------
class AdminOverviewDTO(BaseDTO):
    total_students: int = 0
    total_teachers: int = 0
    total_classes: int = 0
    total_subjects: int = 0
    today_lessons: int = 0


# -----------------------------
# Attendance
# -----------------------------
class AdminAttendanceStatusSummaryDTO(BaseDTO):
    status: str
    count: int = 0


class AdminAttendanceDailyTrendDTO(BaseDTO):
    # Expect ISO date string from backend like "2025-12-27"
    # Pydantic parses to dt.date and serializes back to ISO.
    date: dt.date
    present: int = 0
    absent: int = 0
    excused: int = 0
    total: int = 0


class AdminAttendanceByClassDTO(BaseDTO):
    class_id: str
    class_name: str = "Unknown"
    present: int = 0
    absent: int = 0
    excused: int = 0
    total: int = 0


class LocalizedNameDTO(BaseDTO):
    en: Optional[str] = None
    kh: Optional[str] = None

class AdminTopAbsentStudentDTO(BaseDTO):
    student_id: str
    student_name: str = "Unknown"

    student_name_en: Optional[str] = None
    student_name_kh: Optional[str] = None

    class_id: Optional[str] = None
    class_name: Optional[str] = None
    absent_count: int = 0
    total_records: Optional[int] = None

    @model_validator(mode="before")
    @classmethod
    def normalize_student_name(cls, data: Any):
        if not isinstance(data, dict):
            return data

        name = data.get("student_name")
        if isinstance(name, dict):
            en = name.get("en")
            kh = name.get("kh")
            data["student_name_en"] = data.get("student_name_en") or en
            data["student_name_kh"] = data.get("student_name_kh") or kh
            data["student_name"] = (en or kh or data.get("student_name") or "Unknown")

        return data
class AdminAttendanceDashboardDTO(BaseDTO):
    status_summary: List[AdminAttendanceStatusSummaryDTO] = Field(default_factory=list)
    daily_trend: List[AdminAttendanceDailyTrendDTO] = Field(default_factory=list)
    by_class: List[AdminAttendanceByClassDTO] = Field(default_factory=list)
    top_absent_students: List[AdminTopAbsentStudentDTO] = Field(default_factory=list)


# -----------------------------
# Grades
# -----------------------------
class AdminAvgScoreBySubjectDTO(BaseDTO):
    subject_id: str
    subject_name: str = "Unknown"
    avg_score: float = 0.0
    sample_size: int = 0


class AdminGradeDistributionBucketDTO(BaseDTO):
    range: str
    count: int = 0


class AdminPassRateByClassDTO(BaseDTO):
    class_id: str
    class_name: str = "Unknown"
    avg_score: float = 0.0
    pass_rate: float = 0.0  # 0..1
    total_students: int = 0
    passed: int = 0


class AdminGradeDashboardDTO(BaseDTO):
    avg_score_by_subject: List[AdminAvgScoreBySubjectDTO] = Field(default_factory=list)
    grade_distribution: List[AdminGradeDistributionBucketDTO] = Field(default_factory=list)
    pass_rate_by_class: List[AdminPassRateByClassDTO] = Field(default_factory=list)


# -----------------------------
# Schedule
# -----------------------------
class AdminLessonsByWeekdayDTO(BaseDTO):
    day_of_week: int
    label: str
    lessons: int = 0


class AdminLessonsByTeacherDTO(BaseDTO):
    teacher_id: str
    teacher_name: str = "Unknown"
    lessons: int = 0
    classes: int = 0


class AdminScheduleDashboardDTO(BaseDTO):
    lessons_by_weekday: List[AdminLessonsByWeekdayDTO] = Field(default_factory=list)
    lessons_by_teacher: List[AdminLessonsByTeacherDTO] = Field(default_factory=list)


# -----------------------------
# Root Dashboard
# -----------------------------
class AdminDashboardDTO(BaseDTO):
    overview: AdminOverviewDTO = Field(default_factory=AdminOverviewDTO)
    attendance: AdminAttendanceDashboardDTO = Field(default_factory=AdminAttendanceDashboardDTO)
    grades: AdminGradeDashboardDTO = Field(default_factory=AdminGradeDashboardDTO)
    schedule: AdminScheduleDashboardDTO = Field(default_factory=AdminScheduleDashboardDTO)