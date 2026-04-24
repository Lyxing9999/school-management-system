from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.contexts.admin.data_transfer.responses.common import PaginatedDTO
from app.contexts.shared.lifecycle.dto import LifecycleDTO


class PayrollRunDTO(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",
        populate_by_name=True,
    )

    id: str
    month: str
    payroll_month: str | None = None
    payroll_run_label: str | None = None
    generated_by: str
    generated_by_name: str | None = None
    created_by: str | None = None
    created_by_name: str | None = None
    deleted_by: str | None = None
    deleted_by_name: str | None = None
    status: str
    lifecycle: LifecycleDTO


class PayslipDTO(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",
        populate_by_name=True,
    )

    id: str
    payroll_run_id: str
    payroll_month: str | None = None
    payroll_run_label: str | None = None
    employee_id: str
    employee_name: str | None = None
    month: str
    base_salary: float
    payable_working_days: int
    paid_holiday_days: int
    unpaid_leave_days: int
    total_ot_hours: float
    ot_payment: float
    total_deductions: float
    net_salary: float
    status: str
    created_by: str | None = None
    created_by_name: str | None = None
    deleted_by: str | None = None
    deleted_by_name: str | None = None
    lifecycle: LifecycleDTO


class PayrollRunPaginatedDTO(PaginatedDTO[PayrollRunDTO]):
    pass


class PayslipPaginatedDTO(PaginatedDTO[PayslipDTO]):
    pass


class GeneratePayrollMetaDTO(BaseModel):
    employee_count: int = 0
    generated_count: int = 0
    skipped_employees: list[dict] = Field(default_factory=list)
    total_amount: float | None = None


class GeneratePayrollResultDTO(BaseModel):
    payroll_run: PayrollRunDTO
    payslips: list[PayslipDTO]
    meta: GeneratePayrollMetaDTO | None = None

    # Legacy flat fields kept for backward compatibility with older UI clients.
    id: str | None = None
    run_id: str | None = None
    month: str | None = None
    payroll_month: str | None = None
    payroll_run_label: str | None = None
    status: str | None = None
    generated_by: str | None = None
    generated_by_name: str | None = None
    total_employees: int | None = None
    generated_count: int | None = None
    total_amount: float | None = None
    generated_at: str | None = None
