from __future__ import annotations

from app.contexts.hrms.domain.audit_log import AuditLog
from app.contexts.shared.time_utils import utc_now


class RejectLeaveRequestUseCase:
    def __init__(
        self,
        *,
        leave_repository,
        employee_repository=None,
        audit_log_repository=None,
        notification_service=None,
    ) -> None:
        self.leave_repository = leave_repository
        self.employee_repository = employee_repository
        self.audit_log_repository = audit_log_repository
        self.notification_service = notification_service

    def execute(self, *, leave_id, manager_user_id, comment: str | None = None):
        leave = self.leave_repository.find_by_id(leave_id)
        leave.reject(manager_id=manager_user_id, comment=comment)
        saved = self.leave_repository.save(leave)
        self._write_audit_log(
            action="leave_rejected",
            actor_id=manager_user_id,
            entity_id=saved.id,
            details={
                "employee_id": str(saved.employee_id),
                "comment": comment,
            },
        )
        if self.notification_service:
            self.notification_service.notify_leave_reviewed(
                leave_id=saved.id,
                employee_id=saved.employee_id,
                approved=False,
                reviewer_user_id=manager_user_id,
                comment=comment,
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
