from __future__ import annotations

from app.contexts.hrms.domain.overtime import (
    OvertimeRequest,
    OvertimeDayType,
)
from app.contexts.hrms.errors.employee_exceptions import (
    EmployeeInactiveException,
    EmployeeNotFoundException,
    EmployeeScheduleNotAssignedException,
)
from app.contexts.hrms.errors.overtime_exceptions import (
    InvalidLocalizedOvertimeTimeRangeException,
    InvalidOvertimeTimeRangeException,
    OverlappingOvertimeRequestException,
    OvertimeEndTimeInvalidException,
    OvertimeRequestDateMismatchException,
    WorkingDayOvertimeStartInvalidException,
)
from app.contexts.hrms.errors.schedule_exceptions import WorkingScheduleNotFoundException
from app.contexts.hrms.domain.audit_log import AuditLog
from app.contexts.shared.time_utils import ensure_utc, to_cambodia
from app.contexts.shared.time_utils import utc_now


class CreateOvertimeRequestUseCase:
    def __init__(
        self,
        *,
        employee_repository,
        working_schedule_repository,
        public_holiday_repository,
        overtime_repository,
        audit_log_repository=None,
    ) -> None:
        self.employee_repository = employee_repository
        self.working_schedule_repository = working_schedule_repository
        self.public_holiday_repository = public_holiday_repository
        self.overtime_repository = overtime_repository
        self.audit_log_repository = audit_log_repository

    def execute(self, *, employee_id, payload):
        employee = self.employee_repository.find_by_id(employee_id)
        if not employee:
            raise EmployeeNotFoundException(str(employee_id))

        employee_status = str(employee.get("status") or "inactive")
        if employee_status != "active":
            raise EmployeeInactiveException(str(employee_id), employee_status)

        schedule_id = employee.get("schedule_id")
        if not schedule_id:
            raise EmployeeScheduleNotAssignedException(str(employee_id))

        schedule = self.working_schedule_repository.find_by_id(schedule_id)
        if not schedule:
            raise WorkingScheduleNotFoundException(schedule_id)

        start_time_utc = ensure_utc(payload.start_time)
        end_time_utc = ensure_utc(payload.end_time)

        if not start_time_utc or not end_time_utc:
            raise InvalidOvertimeTimeRangeException()

        if end_time_utc <= start_time_utc:
            raise OvertimeEndTimeInvalidException()

        start_time_local = to_cambodia(start_time_utc)
        end_time_local = to_cambodia(end_time_utc)

        if not start_time_local or not end_time_local:
            raise InvalidLocalizedOvertimeTimeRangeException()

        request_date_local = start_time_local.date()

        # Optional strict consistency check
        if payload.request_date != request_date_local:
            raise OvertimeRequestDateMismatchException(payload.request_date, request_date_local)

        day_type = self._resolve_day_type(
            request_date=payload.request_date,
            schedule=schedule,
        )

        schedule_end_time_local = start_time_local.replace(
            hour=schedule.end_time.hour,
            minute=schedule.end_time.minute,
            second=getattr(schedule.end_time, "second", 0),
            microsecond=0,
        )

        if (
            day_type == OvertimeDayType.WORKING_DAY
            and start_time_local < schedule_end_time_local
        ):
            raise WorkingDayOvertimeStartInvalidException()

        overlap = self.overtime_repository.find_overlapping_request(
            employee_id=employee["_id"],
            request_date=payload.request_date,
            start_time=start_time_utc,
            end_time=end_time_utc,
        )
        if overlap:
            raise OverlappingOvertimeRequestException(
                str(employee["_id"]),
                payload.request_date,
            )

        schedule_end_time_utc = ensure_utc(schedule_end_time_local)

        ot = OvertimeRequest(
            employee_id=employee["_id"],
            request_date=payload.request_date,
            start_time=start_time_utc,
            end_time=end_time_utc,
            schedule_end_time=schedule_end_time_utc,
            reason=payload.reason,
            day_type=day_type,
            basic_salary=float(employee.get("basic_salary") or 0),
        )

        saved = self.overtime_repository.save(ot)

        self._write_audit_log(
            action="ot_submitted",
            actor_id=employee.get("user_id"),
            entity_id=saved.id,
            details={
                "employee_id": str(saved.employee_id),
                "request_date": str(saved.request_date),
                "day_type": (
                    saved.day_type.value
                    if hasattr(saved.day_type, "value")
                    else str(saved.day_type)
                ),
            },
        )

        return saved

    def _resolve_day_type(self, *, request_date, schedule):
        holiday = self.public_holiday_repository.find_by_date(request_date)
        if holiday and not holiday.is_deleted():
            return OvertimeDayType.PUBLIC_HOLIDAY

        if schedule.is_weekend(request_date.weekday()):
            return OvertimeDayType.WEEKEND

        return OvertimeDayType.WORKING_DAY

    def _write_audit_log(self, *, action: str, actor_id, entity_id, details: dict) -> None:
        if not self.audit_log_repository:
            return

        audit_log = AuditLog(
            id=None,
            entity_type="overtime",
            entity_id=entity_id,
            action=action,
            actor_id=actor_id,
            action_at=utc_now(),
            details=details,
        )
        self.audit_log_repository.save(audit_log)
