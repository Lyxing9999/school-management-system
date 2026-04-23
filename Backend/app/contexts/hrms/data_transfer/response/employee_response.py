from __future__ import annotations

from typing import Optional, Dict, Any

from pydantic import BaseModel, ConfigDict

from app.contexts.shared.lifecycle.dto import LifecycleDTO
from app.contexts.admin.data_transfer.responses.common import PaginatedDTO
from app.contexts.iam.data_transfer.response import IAMBaseDataDTO


class EmployeeDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore", populate_by_name=True)

    id: str
    employee_name: Optional[str] = None
    user_id: Optional[str] = None
    account_name: Optional[str] = None
    account_email: Optional[str] = None

    employee_code: str
    full_name: str
    department: Optional[str] = None
    position: Optional[str] = None

    employment_type: str
    basic_salary: float
    contract: Optional[Dict[str, Any]] = None
    work_location_id: str | None = None
    work_location_name: Optional[str] = None
    manager_user_id: Optional[str] = None
    manager_name: Optional[str] = None
    schedule_id: Optional[str] = None
    schedule_name: Optional[str] = None
    status: str

    created_by: Optional[str] = None
    created_by_name: Optional[str] = None
    deleted_by: Optional[str] = None
    deleted_by_name: Optional[str] = None
    photo_url: Optional[str] = None

    lifecycle: LifecycleDTO


class EmployeePaginatedDTO(PaginatedDTO[EmployeeDTO]):
    pass


class EmployeeWithAccountDTO(BaseModel):
    employee: EmployeeDTO
    user: IAMBaseDataDTO







class EmployeeAccountSummaryDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore", populate_by_name=True)

    id: str
    user_id: Optional[str] = None
    email: Optional[str] = None
    account_email: Optional[str] = None
    username: Optional[str] = None
    account_name: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None


class EmployeeWithAccountSummaryDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore", populate_by_name=True)

    employee: EmployeeDTO
    account: Optional[EmployeeAccountSummaryDTO] = None


class EmployeeWithAccountSummaryPaginatedDTO(PaginatedDTO[EmployeeWithAccountSummaryDTO]):
    pass
