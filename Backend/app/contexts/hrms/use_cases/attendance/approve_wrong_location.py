from __future__ import annotations

from app.contexts.hrms.domain.audit_log import AuditLog
from app.contexts.hrms.errors.attendance_exceptions import (
    AttendanceNotFoundException,
    AttendanceWrongLocationReviewNotAllowedException,
    AttendanceWrongLocationReviewStateException,
)
from app.contexts.shared.time_utils import utc_now
from app.contexts.shared.model_converter import mongo_converter


class ApproveWrongLocationUseCase:
    def __init__(
        self,
        *,
        attendance_repository,
        employee_repository=None,
        audit_log_repository=None,
        notification_service=None,
    ) -> None:
        self.attendance_repository = attendance_repository
        self.employee_repository = employee_repository
        self.audit_log_repository = audit_log_repository
        self.notification_service = notification_service

    def execute(
        self,
        *,
        attendance_id,
        admin_id,
        actor_role: str | None = None,
        approved: bool,
        comment: str | None = None,
        location_id: str | None = None,
    ):
        attendance = self.attendance_repository.find_by_id(attendance_id)
        if not attendance:
            raise AttendanceNotFoundException(attendance_id)

        normalized_role = str(actor_role or "").strip().lower()
        is_manager = normalized_role == "manager"
        if is_manager and self.employee_repository:
            employee = self.employee_repository.find_by_id(attendance.employee_id)
            employee_manager_user_id = employee.get("manager_user_id") if employee else None
            if (
                not employee_manager_user_id
                or str(employee_manager_user_id) != str(admin_id)
            ):
                raise AttendanceWrongLocationReviewNotAllowedException(
                    manager_user_id=str(admin_id),
                    employee_manager_user_id=(
                        str(employee_manager_user_id) if employee_manager_user_id else None
                    ),
                )

        current_review_status = (
            attendance.location_review_status.value
            if hasattr(attendance.location_review_status, "value")
            else str(attendance.location_review_status)
        )

        if current_review_status != "pending":
            raise AttendanceWrongLocationReviewStateException(
                attendance_id=attendance_id,
                current_status=current_review_status,
            )

        if location_id is not None:
            attendance.location_id = mongo_converter.convert_to_object_id(location_id)

        if approved:
            attendance.approve_wrong_location(
                admin_id=admin_id,
                comment=comment,
            )

            action = "attendance_wrong_location_approved"
        else:
            attendance.reject_wrong_location(
                admin_id=admin_id,
                comment=comment,
            )
            action = "attendance_wrong_location_rejected"

        updated = self.attendance_repository.save(attendance)

        self._write_audit_log(
            action=action,
            actor_id=admin_id,
            entity_id=updated.id,
            details={
                "approved": approved,
                "comment": comment,
                "location_id": location_id,
                "status": (
                    updated.status.value
                    if hasattr(updated.status, "value")
                    else str(updated.status)
                ),
                "location_review_status": (
                    updated.location_review_status.value
                    if hasattr(updated.location_review_status, "value")
                    else str(updated.location_review_status)
                ),
                "attendance_date": (
                    updated.attendance_date.isoformat()
                    if updated.attendance_date
                    else None
                ),
                "employee_id": str(updated.employee_id),
                "reviewed_by_role": normalized_role or None,
            },
        )
        if self.notification_service:
            self.notification_service.notify_wrong_location_reviewed(
                attendance_id=updated.id,
                employee_id=updated.employee_id,
                approved=approved,
                reviewer_user_id=admin_id,
                comment=comment,
            )

        return updated

    def _write_audit_log(self, *, action: str, actor_id, entity_id, details: dict) -> None:
        if not self.audit_log_repository:
            return

        audit_log = AuditLog(
            id=None,
            entity_type="attendance",
            entity_id=entity_id,
            action=action,
            actor_id=actor_id,
            action_at=utc_now(),
            details=details,
        )
        self.audit_log_repository.save(audit_log)
