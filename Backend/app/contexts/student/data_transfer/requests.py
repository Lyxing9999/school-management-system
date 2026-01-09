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



class StudentGradesFilterSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")

    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=100)

    class_id: Optional[str] = None
    subject_id: Optional[str] = None
    term: Optional[str] = None  # "2025-S1"

    grade_type: Optional[str] = None
    q: Optional[str] = None