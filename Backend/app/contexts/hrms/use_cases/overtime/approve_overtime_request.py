from __future__ import annotations

from app.contexts.hrms.domain.audit_log import AuditLog
from app.contexts.shared.time_utils import utc_now


class ApproveOvertimeRequestUseCase:
    def __init__(self, *, overtime_repository, audit_log_repository=None) -> None:
        self.overtime_repository = overtime_repository
        self.audit_log_repository = audit_log_repository

    def execute(
        self,
        *,
        overtime_id,
        manager_id,
        actor_user_id=None,
        actor_role: str | None = None,
        approved_hours: float | None = None,
        comment: str | None = None,
    ):
        ot = self.overtime_repository.find_by_id(overtime_id)

        ot.approve(
            manager_id=manager_id,
            approved_hours=approved_hours,
            comment=comment,
        )

        saved = self.overtime_repository.save(ot)
        self._write_audit_log(
            action="ot_approved",
            actor_id=actor_user_id or manager_id,
            entity_id=saved.id,
            details={
                "employee_id": str(saved.employee_id),
                "approved_by_role": str(actor_role or "").strip().lower() or None,
                "approved_hours": float(saved.approved_hours),
                "comment": comment,
            },
        )
        return saved

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
