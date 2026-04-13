from __future__ import annotations

from ..value_objects.attendance_status import AttendanceStatus
from ..value_objects.review_status import ReviewStatus


class AttendanceStatusResolver:
    @staticmethod
    def resolve_after_check_out(*, attendance) -> AttendanceStatus:
        if attendance.location_review_status == ReviewStatus.REJECTED:
            # TODO choose system policy here
            return AttendanceStatus.CHECKED_OUT

        if attendance.early_leave_minutes > 0:
            return AttendanceStatus.EARLY_LEAVE

        if attendance.late_minutes > 0:
            return AttendanceStatus.LATE

        return AttendanceStatus.CHECKED_OUT