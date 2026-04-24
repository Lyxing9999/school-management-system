from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict





class AttendanceDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")

    id: str
    employee_id: str
    employee_name: Optional[str] = None
    attendance_date: Optional[date] = None

    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None

    schedule_id: Optional[str] = None
    schedule_name: Optional[str] = None
    location_id: Optional[str] = None
    location_name: Optional[str] = None

    check_in_latitude: Optional[float] = None
    check_in_longitude: Optional[float] = None
    check_out_latitude: Optional[float] = None
    check_out_longitude: Optional[float] = None

    day_type: str
    is_ot_eligible: bool
    status: str
    notes: Optional[str] = None

    late_minutes: int
    early_leave_minutes: int

    wrong_location_reason: Optional[str] = None
    location_review_status: str
    wrong_location_status: Optional[str] = None

    late_reason: Optional[str] = None
    early_leave_reason: Optional[str] = None
    early_leave_review_status: str

    admin_comment: Optional[str] = None
    location_reviewed_by: Optional[str] = None
    location_reviewed_by_name: Optional[str] = None
    early_leave_reviewed_by: Optional[str] = None
    early_leave_reviewed_by_name: Optional[str] = None
    created_by: Optional[str] = None
    created_by_name: Optional[str] = None
    deleted_by: Optional[str] = None
    deleted_by_name: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class PaginationDTO(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int


class AttendancePaginatedDTO(BaseModel):
    items: list[AttendanceDTO]
    pagination: PaginationDTO


class AttendanceTodayDTO(BaseModel):
    item: AttendanceDTO | None = None
