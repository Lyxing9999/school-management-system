from __future__ import annotations

from datetime import datetime

from app.contexts.hrms.domain.attendance import Attendance, AttendanceDayType
from app.contexts.hrms.domain.audit_log import AuditLog
from app.contexts.hrms.domain.work_location import WorkLocation
from app.contexts.hrms.domain.working_schedule import WorkingSchedule
from app.contexts.hrms.errors.attendance_exceptions import (
    AlreadyCheckedInTodayException,
    LateReasonRequiredException,
    LocationValidationException,
    NotScheduledWorkingDayException,
    UnpaidPublicHolidayCheckInNotAllowedException,
)
from app.contexts.hrms.errors.employee_exceptions import (
    EmployeeInactiveException,
    EmployeeNotFoundException,
    EmployeeScheduleNotAssignedException,
)
from app.contexts.hrms.errors.location_exceptions import (
    WorkLocationInactiveException,
    WorkLocationNotFoundException,
)
from app.contexts.hrms.errors.schedule_exceptions import WorkingScheduleNotFoundException
from app.contexts.shared.lifecycle.domain import Lifecycle
from app.contexts.shared.time_utils import (
    ensure_utc,
    utc_now,
    to_cambodia,
    cambodia_start_of_day_as_utc,
)


class CheckInEmployeeUseCase:
    LATE_REASON_THRESHOLD_MINUTES = 1

    def __init__(
        self,
        *,
        employee_repository,
        working_schedule_repository,
        work_location_repository,
        public_holiday_repository,
        attendance_repository,
        audit_log_repository=None,
    ) -> None:
        self.employee_repository = employee_repository
        self.working_schedule_repository = working_schedule_repository
        self.work_location_repository = work_location_repository
        self.public_holiday_repository = public_holiday_repository
        self.attendance_repository = attendance_repository
        self.audit_log_repository = audit_log_repository

    def execute(
        self,
        *,
        employee_id,
        check_in_time: datetime,
        latitude: float,
        longitude: float,
        wrong_location_reason: str | None = None,
        late_reason: str | None = None,
    ) -> Attendance:
        employee = self._get_employee(employee_id)
        schedule = self._get_schedule(employee)
        location = self._get_work_location(employee)

        check_in_time_utc = ensure_utc(check_in_time)
        check_in_time_local = to_cambodia(check_in_time_utc)
        attendance_date_utc = cambodia_start_of_day_as_utc(check_in_time_utc)

        day_type = self._resolve_day_type(
            schedule=schedule,
            check_in_time_local=check_in_time_local,
            employee_id=employee["_id"],
        )

        self._ensure_not_checked_in(
            employee_id=employee["_id"],
            attendance_date=attendance_date_utc,
        )

        is_valid_location = self._is_valid_location(
            location=location,
            latitude=latitude,
            longitude=longitude,
        )

        if not is_valid_location and not (wrong_location_reason or "").strip():
            raise LocationValidationException(
                message="wrong_location_reason is required when check-in location is invalid",
                details={
                    "employee_id": str(employee["_id"]),
                    "latitude": latitude,
                    "longitude": longitude,
                },
            )

        late_minutes = 0
        if day_type == AttendanceDayType.WORKING_DAY:
            late_minutes = self._calculate_late_minutes(
                schedule=schedule,
                check_in_time=check_in_time_utc,
            )

        if (
            day_type == AttendanceDayType.WORKING_DAY
            and late_minutes >= self.LATE_REASON_THRESHOLD_MINUTES
            and not (late_reason or "").strip()
        ):
            raise LateReasonRequiredException(employee["_id"])

        now = utc_now()

        attendance = Attendance.create_for_day(
            employee_id=employee["_id"],
            attendance_date=attendance_date_utc,
            schedule_id=schedule.id,
            location_id=location.id if location else None,
            day_type=day_type,
            is_ot_eligible=day_type in {
                AttendanceDayType.WEEKEND,
                AttendanceDayType.PUBLIC_HOLIDAY,
            },
            lifecycle=Lifecycle(
                created_at=now,
                updated_at=now,
                deleted_at=None,
                deleted_by=None,
            ),
        )

        attendance.check_in(
            check_in_time=check_in_time_utc,
            latitude=latitude,
            longitude=longitude,
            is_valid_location=is_valid_location,
            reason=wrong_location_reason,
        )

        if late_minutes > 0:
            attendance.mark_late(late_minutes)
            attendance.late_reason = (late_reason or "").strip() or None

        attendance = self.attendance_repository.save(attendance)

        self._write_audit_log(
            action="attendance_check_in",
            actor_id=employee["_id"],
            entity_id=attendance.id,
            details={
                "status": attendance.status.value if hasattr(attendance.status, "value") else str(attendance.status),
                "day_type": attendance.day_type.value if hasattr(attendance.day_type, "value") else str(attendance.day_type),
                "is_ot_eligible": attendance.is_ot_eligible,
                "late_minutes": attendance.late_minutes,
                "late_reason": attendance.late_reason,
                "location_review_status": (
                    attendance.location_review_status.value
                    if hasattr(attendance.location_review_status, "value")
                    else str(attendance.location_review_status)
                ),
                "attendance_date": attendance.attendance_date.isoformat() if attendance.attendance_date else None,
                "check_in_time": attendance.check_in_time.isoformat() if attendance.check_in_time else None,
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

    def _get_schedule(self, employee: dict) -> WorkingSchedule:
        schedule_id = employee.get("schedule_id")
        if not schedule_id:
            raise EmployeeScheduleNotAssignedException(str(employee.get("_id")))

        schedule = self.working_schedule_repository.find_by_id(schedule_id)
        if not schedule:
            raise WorkingScheduleNotFoundException(schedule_id)

        return schedule

    def _get_work_location(self, employee: dict) -> WorkLocation | None:
        location_id = employee.get("work_location_id")
        if location_id:
            location = self.work_location_repository.find_by_id(location_id)
            if not location:
                raise WorkLocationNotFoundException(str(location_id))
            if not location.is_active:
                raise WorkLocationInactiveException(str(location_id))
            return location
        return self._get_default_location()

    def _get_default_location(self) -> WorkLocation | None:
        if hasattr(self.work_location_repository, "find_active_default"):
            return self.work_location_repository.find_active_default()
        if hasattr(self.work_location_repository, "find_default"):
            return self.work_location_repository.find_default()
        if hasattr(self.work_location_repository, "list_locations"):
            items = self.work_location_repository.list_locations(is_active=True)
            return items[0] if items else None
        return None

    def _resolve_day_type(
        self,
        *,
        schedule: WorkingSchedule,
        check_in_time_local: datetime,
        employee_id,
    ) -> AttendanceDayType:
        holiday = self.public_holiday_repository.find_by_date(check_in_time_local.date())
        if holiday:
            if not holiday.is_paid:
                raise UnpaidPublicHolidayCheckInNotAllowedException(
                    employee_id=employee_id,
                    holiday_date=check_in_time_local.date().isoformat(),
                )
            return AttendanceDayType.PUBLIC_HOLIDAY

        weekday_value = check_in_time_local.weekday()

        if schedule.is_weekend(weekday_value):
            return AttendanceDayType.WEEKEND

        if schedule.is_working_day(weekday_value):
            return AttendanceDayType.WORKING_DAY

        raise NotScheduledWorkingDayException(
            employee_id=employee_id,
            weekday_value=weekday_value,
        )

    def _ensure_not_checked_in(self, *, employee_id, attendance_date) -> None:
        existing = self.attendance_repository.find_by_employee_and_date(
            employee_id,
            attendance_date,
        )
        if existing:
            raise AlreadyCheckedInTodayException(employee_id)

    def _is_valid_location(
        self,
        *,
        location: WorkLocation | None,
        latitude: float,
        longitude: float,
    ) -> bool:
        if not location:
            return True
        return location.contains(latitude, longitude)

    def _calculate_late_minutes(self, *, schedule: WorkingSchedule, check_in_time: datetime) -> int:
        check_in_time_local = to_cambodia(check_in_time)
        start_time = schedule.start_time

        if hasattr(start_time, "hour"):
            schedule_start = check_in_time_local.replace(
                hour=start_time.hour,
                minute=start_time.minute,
                second=getattr(start_time, "second", 0),
                microsecond=0,
            )
        else:
            hh, mm, *rest = str(start_time).split(":")
            ss = int(rest[0]) if rest else 0
            schedule_start = check_in_time_local.replace(
                hour=int(hh),
                minute=int(mm),
                second=ss,
                microsecond=0,
            )

        if check_in_time_local <= schedule_start:
            return 0

        return int((check_in_time_local - schedule_start).total_seconds() // 60)

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