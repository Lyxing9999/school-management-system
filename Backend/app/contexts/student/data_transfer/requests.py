from __future__ import annotations
from datetime import date
from typing import Optional, Literal

from pydantic import BaseModel, Field, ConfigDict


class StudentAttendanceFilterSchema(BaseModel):
    """
    Used for: GET /student/me/attendance
    Query/body filter for student's own attendance.
    """
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="ignore",
    )

    class_id: Optional[str] = Field(
        None,
        description="Filter by class id (optional)",
    )
    status: Optional[Literal["present", "absent", "excused"]] = Field(
        None,
        description="Optional status filter",
    )
    from_date: Optional[date] = Field(
        None,
        description="Start date (inclusive) for range filter",
    )
    to_date: Optional[date] = Field(
        None,
        description="End date (inclusive) for range filter",
    )


class StudentGradesFilterSchema(BaseModel):
    """
    Used for: GET /student/me/grades
    """
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="ignore",
    )

    class_id: Optional[str] = Field(
        None,
        description="Filter by class id (optional)",
    )
    subject_id: Optional[str] = Field(
        None,
        description="Filter by subject id (optional)",
    )
    term: Optional[str] = Field(
        None,
        description="Filter by term, e.g. '2025-S1' (optional)",
    )


class StudentScheduleFilterSchema(BaseModel):
    """
    Used for: GET /student/me/schedule
    """
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="ignore",
    )

    day_of_week: Optional[int] = Field(
        None,
        ge=1,
        le=7,
        description="1=Monday, 7=Sunday (optional)",
    )
    class_id: Optional[str] = Field(
        None,
        description="Filter by specific class (optional)",
    )

