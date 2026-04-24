from __future__ import annotations

from app.contexts.hrms.domain.audit_log import AuditLog
from app.contexts.shared.time_utils import utc_now


class RejectOvertimeRequestUseCase:
    def __init__(
        self,
        *,
        overtime_repository,
        employee_repository=None,
        audit_log_repository=None,
        notification_service=None,
    ) -> None:
        self.overtime_repository = overtime_repository
        self.employee_repository = employee_repository
        self.audit_log_repository = audit_log_repository
        self.notification_service = notification_service

    def execute(
        self,
        *,
        overtime_id,
        manager_id,
        actor_user_id=None,
        actor_role: str | None = None,
        comment: str | None = None,
    ):
        ot = self.overtime_repository.find_by_id(overtime_id)

        ot.reject(
            manager_id=manager_id,
            comment=comment,
        )

        saved = self.overtime_repository.save(ot)
        self._write_audit_log(
            action="ot_rejected",
            actor_id=actor_user_id or manager_id,
            entity_id=saved.id,
            details={
                "employee_id": str(saved.employee_id),
                "rejected_by_role": str(actor_role or "").strip().lower() or None,
                "comment": comment,
            },
        )
        if self.notification_service:
            self.notification_service.notify_overtime_reviewed(
                overtime_id=saved.id,
                employee_id=saved.employee_id,
                approved=False,
                reviewer_user_id=actor_user_id or manager_id,
                comment=comment,
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
