from __future__ import annotations

from app.contexts.hrms.domain.audit_log import AuditLog
from app.contexts.hrms.errors.leave_exceptions import (
    LeaveEmployeeNotFoundException,
    LeaveReviewNotAllowedException,
)
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

    def execute(
        self,
        *,
        leave_id,
        manager_user_id,
        actor_role: str | None = None,
        comment: str | None = None,
    ):
        leave = self.leave_repository.find_by_id(leave_id)

        employee = self.employee_repository.find_by_id(leave.employee_id)
        if not employee:
            raise LeaveEmployeeNotFoundException(str(leave.employee_id))

        employee_manager_user_id = employee.get("manager_user_id")
        normalized_role = str(actor_role or "").strip().lower()
        is_hr_admin = normalized_role == "hr_admin"
        if (
            not is_hr_admin
            and (
                not employee_manager_user_id
                or str(employee_manager_user_id) != str(manager_user_id)
            )
        ):
            raise LeaveReviewNotAllowedException(
                manager_user_id=str(manager_user_id),
                employee_manager_user_id=(
                    str(employee_manager_user_id) if employee_manager_user_id else None
                ),
            )

        leave.reject(manager_id=manager_user_id, comment=comment)
        saved = self.leave_repository.save(leave)
        self._write_audit_log(
            action="leave_rejected",
            actor_id=manager_user_id,
            entity_id=saved.id,
            details={
                "employee_id": str(saved.employee_id),
                "rejected_by_role": normalized_role or None,
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
