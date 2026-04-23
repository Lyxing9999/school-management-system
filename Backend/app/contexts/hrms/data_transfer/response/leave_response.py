from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.contexts.shared.lifecycle.dto import LifecycleDTO
from app.contexts.admin.data_transfer.responses.common import PaginatedDTO


class LeaveRequestDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore", populate_by_name=True)

    id: str
    employee_id: str
    employee_name: Optional[str] = None
    leave_type: str
    start_date: date
    end_date: date
    reason: str
    contract_start: date
    contract_end: date
    is_paid: bool
    status: str
    manager_user_id: Optional[str] = None
    manager_name: Optional[str] = None
    manager_comment: Optional[str] = None
    created_by: Optional[str] = None
    created_by_name: Optional[str] = None
    deleted_by: Optional[str] = None
    deleted_by_name: Optional[str] = None
    total_days: int
    lifecycle: LifecycleDTO


class LeaveRequestPaginatedDTO(PaginatedDTO[LeaveRequestDTO]):
    pass


class LeaveSummaryDTO(BaseModel):
    total_requests: int
    pending: int
    approved: int
    rejected: int
    cancelled: int
    total_approved_days: int


class LeaveBalanceDTO(BaseModel):
    annual_entitlement: int
    used_days: int
    remaining_days: int
