from __future__ import annotations

from app.contexts.hrms.errors.attendance_exceptions import AlreadyCheckedInTodayException


class CanCheckInPolicy:
    @staticmethod
    def ensure(attendance) -> None:
        if attendance.check_in_time is not None:
            raise AlreadyCheckedInTodayException(attendance.employee_id)