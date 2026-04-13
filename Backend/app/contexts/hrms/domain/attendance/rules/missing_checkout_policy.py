from __future__ import annotations

from app.contexts.shared.time_utils import to_cambodia


class MissingCheckoutPolicy:
    def __init__(self, *, grace_hours: int = 2) -> None:
        self.grace_hours = grace_hours

    def should_mark_missing_checkout(self, *, attendance, schedule, now_utc_dt) -> bool:
        if attendance.check_in_time is None:
            return False

        if attendance.check_out_time is not None:
            return False

        now_local = to_cambodia(now_utc_dt)
        attendance_local = to_cambodia(attendance.attendance_date)

        cutoff_local = attendance_local.replace(
            hour=schedule.end_time.hour + self.grace_hours,
            minute=schedule.end_time.minute,
            second=0,
            microsecond=0,
        )

        return now_local >= cutoff_local