from __future__ import annotations

from app.contexts.hrms.domain.audit_log import AuditLog
from app.contexts.hrms.errors.overtime_exceptions import OvertimeOwnershipRequiredException
from app.contexts.shared.time_utils import utc_now


class CancelOvertimeRequestUseCase:
    def __init__(
        self,
        *,
        overtime_repository,
        employee_repository=None,
        audit_log_repository=None,
    ) -> None:
        self.overtime_repository = overtime_repository
        self.employee_repository = employee_repository
        self.audit_log_repository = audit_log_repository

    def execute(
        self,
        *,
        overtime_id,
        actor_employee_id=None,
        actor_user_id=None,
        actor_role: str | None = None,
    ):
        ot = self.overtime_repository.find_by_id(overtime_id)
        normalized_role = str(actor_role or "").strip().lower()

        if not self._can_cancel(
            overtime_employee_id=ot.employee_id,
            actor_employee_id=actor_employee_id,
            actor_user_id=actor_user_id,
            actor_role=normalized_role,
        ):
            raise OvertimeOwnershipRequiredException(
                actor_id=str(actor_employee_id or actor_user_id or ""),
                overtime_employee_id=str(ot.employee_id),
            )

        ot.cancel(actor_id=actor_employee_id or actor_user_id)
        saved = self.overtime_repository.save(ot)

        self._write_audit_log(
            action="ot_cancelled",
            actor_id=actor_user_id,
            entity_id=saved.id,
            details={
                "employee_id": str(saved.employee_id),
                "cancelled_by_role": normalized_role or None,
            },
        )

        return saved

    def _can_cancel(
        self,
        *,
        overtime_employee_id,
        actor_employee_id=None,
        actor_user_id=None,
        actor_role: str | None = None,
    ) -> bool:
        if actor_employee_id and str(overtime_employee_id) == str(actor_employee_id):
            return True

        role = str(actor_role or "").strip().lower()
        if role == "hr_admin":
            return True

        if role == "manager" and actor_user_id and self.employee_repository:
            employee = self.employee_repository.find_by_id(overtime_employee_id)
            manager_user_id = employee.get("manager_user_id") if employee else None
            if manager_user_id and str(manager_user_id) == str(actor_user_id):
                return True

        return False

    def _write_audit_log(self, *, action: str, actor_id, entity_id, details: dict) -> None:
        if not self.audit_log_repository:
            return

        audit_log = AuditLog(
            id=None,
            entity_type="overtime",
            entity_id=entity_id,
            action=action,
            actor_id=actor_id,
            action_at=utc_now(),
            details=details,
        )
        self.audit_log_repository.save(audit_log)
