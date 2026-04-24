from __future__ import annotations

from datetime import datetime

from app.contexts.hrms.domain.attendance import AttendanceDayType
from app.contexts.hrms.domain.audit_log import AuditLog
from app.contexts.hrms.domain.working_schedule import WorkingSchedule
from app.contexts.hrms.errors.attendance_exceptions import (
    AttendanceAlreadyCheckedOutException,
    AttendanceCheckInRequiredException,
    EarlyLeaveReasonRequiredException,
    InvalidCheckOutTimeException,
)
from app.contexts.hrms.errors.employee_exceptions import (
    EmployeeInactiveException,
    EmployeeNotFoundException,
    EmployeeScheduleNotAssignedException,
)
from app.contexts.hrms.errors.schedule_exceptions import WorkingScheduleNotFoundException
from app.contexts.shared.time_utils import (
    ensure_utc,
    utc_now,
    cambodia_start_of_day_as_utc,
)


class CheckOutEmployeeUseCase:
    EARLY_LEAVE_REASON_THRESHOLD_MINUTES = 1
    REQUIRE_EARLY_LEAVE_APPROVAL = True

    def __init__(
        self,
        *,
        employee_repository,
        working_schedule_repository,
        attendance_repository,
        audit_log_repository=None,
        notification_service=None,
    ) -> None:
        self.employee_repository = employee_repository
        self.working_schedule_repository = working_schedule_repository
        self.attendance_repository = attendance_repository
        self.audit_log_repository = audit_log_repository
        self.notification_service = notification_service

    def execute(
        self,
        *,
        employee_id,
        check_out_time: datetime,
        latitude: float | None = None,
        longitude: float | None = None,
        early_leave_reason: str | None = None,
        actor_user_id=None,
    ):
        employee = self._get_employee(employee_id)

        check_out_time_utc = ensure_utc(check_out_time)
        attendance_date_utc = cambodia_start_of_day_as_utc(check_out_time_utc)

        attendance = self._get_today_attendance(
            employee_id=employee["_id"],
            attendance_date=attendance_date_utc,
        )

        schedule = self._get_schedule(employee)

        if attendance.check_out_time is not None:
            raise AttendanceAlreadyCheckedOutException(attendance.id)

        if attendance.check_in_time is None:
            raise AttendanceCheckInRequiredException(employee["_id"])

        if check_out_time_utc < attendance.check_in_time:
            raise InvalidCheckOutTimeException(attendance.id)

        early_leave_minutes = 0
        if attendance.day_type == AttendanceDayType.WORKING_DAY:
            early_leave_minutes = self._calculate_early_leave_minutes(
                schedule=schedule,
                check_out_time=check_out_time_utc,
            )

        if (
            attendance.day_type == AttendanceDayType.WORKING_DAY
            and early_leave_minutes >= self.EARLY_LEAVE_REASON_THRESHOLD_MINUTES
            and not (early_leave_reason or "").strip()
        ):
            raise EarlyLeaveReasonRequiredException(employee["_id"])

        attendance.check_out(
            check_out_time=check_out_time_utc,
            latitude=latitude,
            longitude=longitude,
            early_leave_minutes=early_leave_minutes,
            early_leave_reason=early_leave_reason,
            require_early_leave_review=(
                self.REQUIRE_EARLY_LEAVE_APPROVAL and early_leave_minutes > 0
            ),
        )

        attendance = self.attendance_repository.save(attendance)

        self._write_audit_log(
            action="attendance_check_out",
            actor_id=actor_user_id or employee.get("user_id") or employee["_id"],
            entity_id=attendance.id,
            details={
                "employee_id": str(attendance.employee_id),
                "status": attendance.status.value if hasattr(attendance.status, "value") else str(attendance.status),
                "day_type": attendance.day_type.value if hasattr(attendance.day_type, "value") else str(attendance.day_type),
                "is_ot_eligible": attendance.is_ot_eligible,
                "early_leave_minutes": attendance.early_leave_minutes,
                "early_leave_reason": attendance.early_leave_reason,
                "early_leave_review_status": (
                    attendance.early_leave_review_status.value
                    if hasattr(attendance.early_leave_review_status, "value")
                    else str(attendance.early_leave_review_status)
                ),
                "location_review_status": (
                    attendance.location_review_status.value
                    if hasattr(attendance.location_review_status, "value")
                    else str(attendance.location_review_status)
                ),
                "attendance_date": attendance.attendance_date.isoformat() if attendance.attendance_date else None,
                "check_out_time": attendance.check_out_time.isoformat() if attendance.check_out_time else None,
                "check_out_latitude": attendance.check_out_latitude,
                "check_out_longitude": attendance.check_out_longitude,
            },
        )

        return attendance

    def _get_employee(self, employee_id):
        employee = self.employee_repository.find_by_id(employee_id)
        if not employee:
            raise EmployeeNotFoundException(str(employee_id))

        status = str(employee.get("status") or "inactive")
        if status != "active":
            raise EmployeeInactiveException(str(employee.get("_id") or employee_id), status)

        return employee

    def _get_today_attendance(self, *, employee_id, attendance_date):
        attendance = self.attendance_repository.find_by_employee_and_date(
            employee_id,
            attendance_date,
        )
        if not attendance:
            raise AttendanceCheckInRequiredException(employee_id)
        return attendance

    def _get_schedule(self, employee: dict) -> WorkingSchedule:
        schedule_id = employee.get("schedule_id")
        if not schedule_id:
            raise EmployeeScheduleNotAssignedException(str(employee.get("_id")))

        schedule = self.working_schedule_repository.find_by_id(schedule_id)
        if not schedule:
            raise WorkingScheduleNotFoundException(schedule_id)

        return schedule

    def _calculate_early_leave_minutes(
        self,
        *,
        schedule: WorkingSchedule,
        check_out_time: datetime,
    ) -> int:
        from app.contexts.shared.time_utils import to_cambodia

        check_out_time_local = to_cambodia(check_out_time)
        end_time = schedule.end_time

        if not end_time:
            return 0

        if hasattr(end_time, "hour"):
            schedule_end = check_out_time_local.replace(
                hour=end_time.hour,
                minute=end_time.minute,
                second=getattr(end_time, "second", 0),
                microsecond=0,
            )
        else:
            hh, mm, *rest = str(end_time).split(":")
            ss = int(rest[0]) if rest else 0
            schedule_end = check_out_time_local.replace(
                hour=int(hh),
                minute=int(mm),
                second=ss,
                microsecond=0,
            )

        if check_out_time_local >= schedule_end:
            return 0

        return int((schedule_end - check_out_time_local).total_seconds() // 60)

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
