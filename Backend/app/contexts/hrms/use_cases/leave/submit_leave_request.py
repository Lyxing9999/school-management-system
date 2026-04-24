from __future__ import annotations

from app.contexts.hrms.domain.leave import LeaveRequest, LeaveType
from app.contexts.hrms.domain.audit_log import AuditLog
from app.contexts.hrms.errors.employee_exceptions import (
    EmployeeInactiveException,
    EmployeeNotFoundException,
)
from app.contexts.hrms.errors.leave_exceptions import (
    LeaveContractPeriodRequiredException,
    LeaveOutsideContractException,
    LeaveOverlapExistsException,
)
from app.contexts.shared.time_utils import coerce_date
from app.contexts.shared.time_utils import utc_now


class SubmitLeaveRequestUseCase:
    def __init__(
        self,
        *,
        employee_repository,
        leave_repository,
        audit_log_repository=None,
        notification_service=None,
    ) -> None:
        self.employee_repository = employee_repository
        self.leave_repository = leave_repository
        self.audit_log_repository = audit_log_repository
        self.notification_service = notification_service

    def execute(self, *, employee_id, payload):
        employee = self.employee_repository.find_by_id(employee_id)
        if not employee:
            raise EmployeeNotFoundException(str(employee_id))

        employee_status = str(employee.get("status") or "inactive")
        if employee_status != "active":
            raise EmployeeInactiveException(str(employee_id), employee_status)

        employment_type = str(employee.get("employment_type") or "").strip().lower()
        contract = employee.get("contract") or {}

        contract_start = coerce_date(contract.get("start_date"))
        contract_end = coerce_date(contract.get("end_date"))

        if employment_type == "contract":
            if not contract_start or not contract_end:
                raise LeaveContractPeriodRequiredException(str(employee["_id"]))

            if payload.start_date < contract_start or payload.end_date > contract_end:
                raise LeaveOutsideContractException(
                    payload.start_date,
                    payload.end_date,
                    contract_start,
                    contract_end,
                )
        else:
            contract_start = payload.start_date
            contract_end = payload.end_date
        overlap = self.leave_repository.find_overlapping_approved_or_pending(
            employee_id=employee["_id"],
            start_date=payload.start_date,
            end_date=payload.end_date,
        )
        if overlap:
            raise LeaveOverlapExistsException(
                str(employee["_id"]),
                payload.start_date,
                payload.end_date,
            )

        is_paid = payload.leave_type in {
            LeaveType.ANNUAL.value,
            LeaveType.SICK.value,
        }

        leave = LeaveRequest(
            employee_id=employee["_id"],
            leave_type=payload.leave_type,
            start_date=payload.start_date,
            end_date=payload.end_date,
            reason=payload.reason,
            contract_start=contract_start,
            contract_end=contract_end,
            is_paid=is_paid,
        )

        saved = self.leave_repository.save(leave)
        self._write_audit_log(
            action="leave_submitted",
            actor_id=employee.get("user_id"),
            entity_id=saved.id,
            details={
                "employee_id": str(saved.employee_id),
                "leave_type": (
                    saved.leave_type.value
                    if hasattr(saved.leave_type, "value")
                    else str(saved.leave_type)
                ),
                "start_date": str(saved.start_date),
                "end_date": str(saved.end_date),
                "total_days": int(saved.total_days()),
            },
        )
        if self.notification_service:
            self.notification_service.notify_leave_submitted(
                leave_id=saved.id,
                employee_id=saved.employee_id,
                leave_type=(
                    saved.leave_type.value
                    if hasattr(saved.leave_type, "value")
                    else str(saved.leave_type)
                ),
                start_date=saved.start_date,
                end_date=saved.end_date,
            )
        return saved

    def _write_audit_log(self, *, action: str, actor_id, entity_id, details: dict) -> None:
        if not self.audit_log_repository:
            return

        audit_log = AuditLog(
            id=None,
            entity_type="leave",
            entity_id=entity_id,
            action=action,
            actor_id=actor_id,
            action_at=utc_now(),
            details=details,
        )
        self.audit_log_repository.save(audit_log)
