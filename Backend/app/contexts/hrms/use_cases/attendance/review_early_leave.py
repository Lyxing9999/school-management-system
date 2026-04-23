from __future__ import annotations

from app.contexts.hrms.errors.attendance_exceptions import AttendanceNotFoundException


class ReviewEarlyLeaveUseCase:
    def __init__(self, *, attendance_repository) -> None:
        self.attendance_repository = attendance_repository

    def execute(
        self,
        *,
        attendance_id,
        admin_id,
        approved: bool,
        comment: str | None = None,
    ):
        attendance = self.attendance_repository.find_by_id(attendance_id)
        if not attendance:
            raise AttendanceNotFoundException(str(attendance_id))

        review_status = "approved" if approved else "rejected"

        fields = {
            "early_leave_review_status": review_status,
            "admin_comment": comment,
            "early_leave_reviewed_by": admin_id,
        }

        return self.attendance_repository.update_fields(attendance_id, fields)