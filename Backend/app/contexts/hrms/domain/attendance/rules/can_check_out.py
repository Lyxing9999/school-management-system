from __future__ import annotations

from datetime import datetime

from app.contexts.hrms.errors.attendance_exceptions import (
    AttendanceAlreadyCheckedOutException,
    AttendanceCheckInRequiredException,
    InvalidCheckOutTimeException,
)


class CanCheckOutPolicy:
    @staticmethod
    def ensure(*, attendance, check_out_time: datetime) -> None:
        if attendance.check_in_time is None:
            raise AttendanceCheckInRequiredException(attendance.employee_id)
        if attendance.check_out_time is not None:
            raise AttendanceAlreadyCheckedOutException(attendance.id)
        if check_out_time < attendance.check_in_time:
            raise InvalidCheckOutTimeException(attendance.id)