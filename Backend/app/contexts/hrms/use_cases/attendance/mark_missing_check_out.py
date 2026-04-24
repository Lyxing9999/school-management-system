from __future__ import annotations

from app.contexts.hrms.domain.audit_log import AuditLog
from app.contexts.hrms.domain.attendance import AttendanceDayType
from app.contexts.shared.time_utils import utc_now, to_cambodia


class MarkMissingCheckOutUseCase:
    GRACE_HOURS = 2

    def __init__(
        self,
        *,
        attendance_repository,
        employee_repository,
        working_schedule_repository,
        audit_log_repository=None,
    ) -> None:
        self.attendance_repository = attendance_repository
        self.employee_repository = employee_repository
        self.working_schedule_repository = working_schedule_repository
        self.audit_log_repository = audit_log_repository

    def execute(self) -> int:
        now_utc_dt = utc_now()
        open_attendances = self.attendance_repository.list_open_attendances()

        updated_count = 0

        for attendance in open_attendances:
            if attendance.day_type != AttendanceDayType.WORKING_DAY:
                continue

            employee = self.employee_repository.find_by_id(attendance.employee_id)
            if not employee:
                continue

            schedule_id = employee.get("schedule_id")
            if not schedule_id:
                continue

            schedule = self.working_schedule_repository.find_by_id(schedule_id)
            if not schedule:
                continue

            if self._should_mark_missing_check_out(
                attendance=attendance,
                schedule=schedule,
                now_utc_dt=now_utc_dt,
            ):
                attendance.mark_missing_check_out()
                self.attendance_repository.save(attendance)

                self._write_audit_log(
                    entity_id=attendance.id,
                    actor_id=employee.get("user_id") or attendance.employee_id,
                    details={
                        "employee_id": str(attendance.employee_id),
                        "status": "missing_check_out",
                        "attendance_date": attendance.attendance_date.isoformat() if attendance.attendance_date else None,
                    },
                )

                updated_count += 1

        return updated_count

    def _should_mark_missing_check_out(self, *, attendance, schedule, now_utc_dt) -> bool:
        if attendance.check_in_time is None:
            return False

        if attendance.check_out_time is not None:
            return False

        now_local = to_cambodia(now_utc_dt)
        attendance_local = to_cambodia(attendance.attendance_date)

        cutoff_local = attendance_local.replace(
            hour=schedule.end_time.hour + self.GRACE_HOURS,
            minute=schedule.end_time.minute,
            second=0,
            microsecond=0,
        )

        return now_local >= cutoff_local

    def _write_audit_log(self, *, entity_id, actor_id, details: dict) -> None:
        if not self.audit_log_repository:
            return

        audit_log = AuditLog(
            id=None,
            entity_type="attendance",
            entity_id=entity_id,
            action="attendance_marked_missing_check_out",
            actor_id=actor_id,
            action_at=utc_now(),
            details=details,
        )
        self.audit_log_repository.save(audit_log)
