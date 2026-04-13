from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time as time_type

from app.contexts.shared.time_utils import to_cambodia


@dataclass(frozen=True)
class ShiftWindow:
    start_time: time_type
    end_time: time_type

    def scheduled_start_local(self, dt_utc: datetime) -> datetime:
        local_dt = to_cambodia(dt_utc)
        return local_dt.replace(
            hour=self.start_time.hour,
            minute=self.start_time.minute,
            second=getattr(self.start_time, "second", 0),
            microsecond=0,
        )

    def scheduled_end_local(self, dt_utc: datetime) -> datetime:
        local_dt = to_cambodia(dt_utc)
        return local_dt.replace(
            hour=self.end_time.hour,
            minute=self.end_time.minute,
            second=getattr(self.end_time, "second", 0),
            microsecond=0,
        )

    def calculate_late_minutes(self, check_in_time_utc: datetime) -> int:
        check_in_local = to_cambodia(check_in_time_utc)
        scheduled_start = self.scheduled_start_local(check_in_time_utc)
        if check_in_local <= scheduled_start:
            return 0
        return int((check_in_local - scheduled_start).total_seconds() // 60)

    def calculate_early_leave_minutes(self, check_out_time_utc: datetime) -> int:
        check_out_local = to_cambodia(check_out_time_utc)
        scheduled_end = self.scheduled_end_local(check_out_time_utc)
        if check_out_local >= scheduled_end:
            return 0
        return int((scheduled_end - check_out_local).total_seconds() // 60)