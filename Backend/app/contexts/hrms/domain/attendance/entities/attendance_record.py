from __future__ import annotations

from datetime import datetime
from bson import ObjectId

from app.contexts.hrms.errors.attendance_exceptions import (
    AttendanceEarlyLeaveReviewStateException,
    AttendanceWrongLocationReviewStateException,
    InvalidLateMinutesException,
)
from app.contexts.shared.lifecycle.domain import Lifecycle, now_utc

from ..rules.attendance_status_resolver import AttendanceStatusResolver
from ..rules.can_check_in import CanCheckInPolicy
from ..rules.can_check_out import CanCheckOutPolicy
from ..rules.wrong_location_policy import WrongLocationPolicy
from ..value_objects.attendance_day_type import AttendanceDayType
from ..value_objects.attendance_status import AttendanceStatus
from ..value_objects.review_status import ReviewStatus


class Attendance:
    @staticmethod
    def _enum_value(value, enum_cls, default=None):
        if value is None:
            return default
        if isinstance(value, enum_cls):
            return value
        if isinstance(value, str):
            return enum_cls(value.strip().lower())
        return enum_cls(value)

    def __init__(
        self,
        *,
        employee_id: ObjectId,
        attendance_date: datetime,
        schedule_id: ObjectId | None = None,
        location_id: ObjectId | None = None,
        day_type: AttendanceDayType | str = AttendanceDayType.WORKING_DAY,
        is_ot_eligible: bool = False,
        id: ObjectId | None = None,
        lifecycle: Lifecycle | None = None,
    ) -> None:
        self.id = id or ObjectId()
        self.employee_id = employee_id
        self.attendance_date = attendance_date
        self.schedule_id = schedule_id
        self.location_id = location_id
        self.day_type = self._enum_value(
            day_type,
            AttendanceDayType,
            AttendanceDayType.WORKING_DAY,
        )
        self.is_ot_eligible = bool(is_ot_eligible)
        self.lifecycle = lifecycle or Lifecycle()

        self.check_in_time: datetime | None = None
        self.check_out_time: datetime | None = None

        self.check_in_latitude: float | None = None
        self.check_in_longitude: float | None = None
        self.check_out_latitude: float | None = None
        self.check_out_longitude: float | None = None

        self.status: AttendanceStatus = AttendanceStatus.CHECKED_IN
        self.notes: str | None = None

        self.late_minutes: int = 0
        self.early_leave_minutes: int = 0

        self.wrong_location_reason: str | None = None
        self.location_review_status: ReviewStatus = ReviewStatus.NOT_REQUIRED

        self.late_reason: str | None = None
        self.early_leave_reason: str | None = None
        self.early_leave_review_status: ReviewStatus = ReviewStatus.NOT_REQUIRED

        self.admin_comment: str | None = None
        self.location_reviewed_by: ObjectId | None = None
        self.early_leave_reviewed_by: ObjectId | None = None

    @classmethod
    def create_for_day(
        cls,
        *,
        employee_id: ObjectId,
        attendance_date: datetime,
        schedule_id: ObjectId | None = None,
        location_id: ObjectId | None = None,
        day_type: AttendanceDayType | str = AttendanceDayType.WORKING_DAY,
        is_ot_eligible: bool = False,
        lifecycle: Lifecycle | None = None,
    ) -> "Attendance":
        return cls(
            employee_id=employee_id,
            attendance_date=attendance_date,
            schedule_id=schedule_id,
            location_id=location_id,
            day_type=day_type,
            is_ot_eligible=is_ot_eligible,
            lifecycle=lifecycle or Lifecycle(),
        )

    @classmethod
    def rehydrate(
        cls,
        *,
        employee_id: ObjectId,
        attendance_date: datetime,
        check_in_time: datetime | None = None,
        check_out_time: datetime | None = None,
        schedule_id: ObjectId | None = None,
        location_id: ObjectId | None = None,
        check_in_latitude: float | None = None,
        check_in_longitude: float | None = None,
        check_out_latitude: float | None = None,
        check_out_longitude: float | None = None,
        status: AttendanceStatus | str = AttendanceStatus.CHECKED_IN,
        day_type: AttendanceDayType | str = AttendanceDayType.WORKING_DAY,
        is_ot_eligible: bool = False,
        notes: str | None = None,
        late_minutes: int = 0,
        early_leave_minutes: int = 0,
        wrong_location_reason: str | None = None,
        location_review_status: ReviewStatus | str = ReviewStatus.NOT_REQUIRED,
        late_reason: str | None = None,
        early_leave_reason: str | None = None,
        early_leave_review_status: ReviewStatus | str = ReviewStatus.NOT_REQUIRED,
        admin_comment: str | None = None,
        location_reviewed_by: ObjectId | None = None,
        early_leave_reviewed_by: ObjectId | None = None,
        id: ObjectId | None = None,
        lifecycle: Lifecycle | None = None,
    ) -> "Attendance":
        obj = cls(
            id=id,
            employee_id=employee_id,
            attendance_date=attendance_date,
            schedule_id=schedule_id,
            location_id=location_id,
            day_type=day_type,
            is_ot_eligible=is_ot_eligible,
            lifecycle=lifecycle or Lifecycle(),
        )

        obj.check_in_time = check_in_time
        obj.check_out_time = check_out_time

        obj.check_in_latitude = check_in_latitude
        obj.check_in_longitude = check_in_longitude
        obj.check_out_latitude = check_out_latitude
        obj.check_out_longitude = check_out_longitude

        obj.status = obj._enum_value(
            status,
            AttendanceStatus,
            AttendanceStatus.CHECKED_IN,
        )
        obj.notes = notes

        obj.late_minutes = int(late_minutes)
        obj.early_leave_minutes = int(early_leave_minutes)

        obj.wrong_location_reason = (wrong_location_reason or "").strip() or None
        obj.location_review_status = obj._enum_value(
            location_review_status,
            ReviewStatus,
            ReviewStatus.NOT_REQUIRED,
        )

        obj.late_reason = (late_reason or "").strip() or None
        obj.early_leave_reason = (early_leave_reason or "").strip() or None
        obj.early_leave_review_status = obj._enum_value(
            early_leave_review_status,
            ReviewStatus,
            ReviewStatus.NOT_REQUIRED,
        )

        obj.admin_comment = (admin_comment or "").strip() or None
        obj.location_reviewed_by = location_reviewed_by
        obj.early_leave_reviewed_by = early_leave_reviewed_by

        obj._normalize_legacy_wrong_location_status()
        return obj

    def _normalize_legacy_wrong_location_status(self) -> None:
        if self.status == AttendanceStatus.WRONG_LOCATION_PENDING:
            self.status = AttendanceStatus.CHECKED_IN
            self.location_review_status = ReviewStatus.PENDING
        elif self.status == AttendanceStatus.WRONG_LOCATION_APPROVED:
            self.status = AttendanceStatus.CHECKED_IN
            self.location_review_status = ReviewStatus.APPROVED
        elif self.status == AttendanceStatus.WRONG_LOCATION_REJECTED:
            self.status = AttendanceStatus.CHECKED_IN
            self.location_review_status = ReviewStatus.REJECTED

    def set_day_type(self, day_type: AttendanceDayType | str) -> None:
        self.day_type = self._enum_value(
            day_type,
            AttendanceDayType,
            AttendanceDayType.WORKING_DAY,
        )
        self.lifecycle.touch(now_utc())

    def mark_ot_eligible(self) -> None:
        self.is_ot_eligible = True
        self.lifecycle.touch(now_utc())

    def clear_ot_eligible(self) -> None:
        self.is_ot_eligible = False
        self.lifecycle.touch(now_utc())

    def check_in(
        self,
        *,
        check_in_time: datetime,
        latitude: float | None = None,
        longitude: float | None = None,
        is_valid_location: bool = True,
        reason: str | None = None,
    ) -> None:
        CanCheckInPolicy.ensure(self)

        self.check_in_time = check_in_time
        self.check_in_latitude = latitude
        self.check_in_longitude = longitude
        self.status = AttendanceStatus.CHECKED_IN

        location_match = WrongLocationPolicy.evaluate(
            is_valid_location=is_valid_location
        )

        if location_match.is_valid:
            self.location_review_status = ReviewStatus.NOT_REQUIRED
            self.wrong_location_reason = None
        else:
            self.location_review_status = ReviewStatus.PENDING
            self.wrong_location_reason = (reason or "").strip() or None

        self.lifecycle.touch(now_utc())

    def check_out(
        self,
        *,
        check_out_time: datetime,
        latitude: float | None = None,
        longitude: float | None = None,
        early_leave_minutes: int = 0,
        early_leave_reason: str | None = None,
        require_early_leave_review: bool = False,
    ) -> None:
        CanCheckOutPolicy.ensure(attendance=self, check_out_time=check_out_time)

        self.check_out_time = check_out_time
        self.check_out_latitude = latitude
        self.check_out_longitude = longitude
        self.early_leave_minutes = int(early_leave_minutes)
        self.early_leave_reason = (early_leave_reason or "").strip() or None

        self.early_leave_review_status = (
            ReviewStatus.PENDING
            if early_leave_minutes > 0 and require_early_leave_review
            else ReviewStatus.NOT_REQUIRED
        )

        self.status = AttendanceStatusResolver.resolve_after_check_out(
            attendance=self
        )
        self.lifecycle.touch(now_utc())

    def mark_late(self, late_minutes: int) -> None:
        if late_minutes < 0:
            raise InvalidLateMinutesException(late_minutes)

        self.late_minutes = int(late_minutes)

        if late_minutes > 0 and self.check_out_time is None:
            self.status = AttendanceStatus.LATE
        elif self.check_out_time is not None:
            self.status = AttendanceStatusResolver.resolve_after_check_out(
                attendance=self
            )

        self.lifecycle.touch(now_utc())

    def approve_wrong_location(
        self,
        *,
        admin_id: ObjectId,
        comment: str | None = None,
    ) -> None:
        if self.location_review_status != ReviewStatus.PENDING:
            raise AttendanceWrongLocationReviewStateException(
                attendance_id=self.id,
                current_status=self.location_review_status.value,
            )

        self.location_review_status = ReviewStatus.APPROVED
        self.location_reviewed_by = admin_id
        self.admin_comment = (comment or "").strip() or None

        if self.check_out_time is not None:
            self.status = AttendanceStatusResolver.resolve_after_check_out(
                attendance=self
            )
        elif self.late_minutes > 0:
            self.status = AttendanceStatus.LATE
        else:
            self.status = AttendanceStatus.CHECKED_IN

        self.lifecycle.touch(now_utc())

    def reject_wrong_location(
        self,
        *,
        admin_id: ObjectId,
        comment: str | None = None,
    ) -> None:
        if self.location_review_status != ReviewStatus.PENDING:
            raise AttendanceWrongLocationReviewStateException(
                attendance_id=self.id,
                current_status=self.location_review_status.value,
            )

        self.location_review_status = ReviewStatus.REJECTED
        self.location_reviewed_by = admin_id
        self.admin_comment = (comment or "").strip() or None

        if self.check_out_time is not None:
            self.status = AttendanceStatusResolver.resolve_after_check_out(
                attendance=self
            )
        elif self.late_minutes > 0:
            self.status = AttendanceStatus.LATE
        else:
            self.status = AttendanceStatus.CHECKED_IN

        self.lifecycle.touch(now_utc())

    def mark_missing_check_out(self) -> None:
        if self.check_in_time is None:
            raise ValueError("Cannot mark missing check-out without check-in")
        if self.check_out_time is not None:
            raise ValueError(
                "Cannot mark missing check-out when check-out already exists"
            )

        self.status = AttendanceStatus.MISSING_CHECK_OUT
        self.day_type = AttendanceDayType.MISSING_CHECK_OUT
        self.lifecycle.touch(now_utc())

    def approve_early_leave(
        self,
        *,
        admin_id: ObjectId,
        comment: str | None = None,
    ) -> None:
        if self.early_leave_review_status != ReviewStatus.PENDING:
            raise AttendanceEarlyLeaveReviewStateException(
                attendance_id=self.id,
                current_status=self.early_leave_review_status.value,
            )

        self.early_leave_review_status = ReviewStatus.APPROVED
        self.early_leave_reviewed_by = admin_id
        self.admin_comment = (comment or "").strip() or None
        self.lifecycle.touch(now_utc())

    def reject_early_leave(
        self,
        *,
        admin_id: ObjectId,
        comment: str | None = None,
    ) -> None:
        if self.early_leave_review_status != ReviewStatus.PENDING:
            raise AttendanceEarlyLeaveReviewStateException(
                attendance_id=self.id,
                current_status=self.early_leave_review_status.value,
            )

        self.early_leave_review_status = ReviewStatus.REJECTED
        self.early_leave_reviewed_by = admin_id
        self.admin_comment = (comment or "").strip() or None
        self.lifecycle.touch(now_utc())

    def mark_absent(self) -> None:
        self.status = AttendanceStatus.ABSENT
        self.lifecycle.touch(now_utc())

    def mark_holiday_off(self) -> None:
        self.status = AttendanceStatus.HOLIDAY_OFF
        self.day_type = AttendanceDayType.PUBLIC_HOLIDAY
        self.is_ot_eligible = False
        self.lifecycle.touch(now_utc())

    def mark_weekend_off(self) -> None:
        self.status = AttendanceStatus.WEEKEND_OFF
        self.day_type = AttendanceDayType.WEEKEND
        self.is_ot_eligible = False
        self.lifecycle.touch(now_utc())

    def total_working_hours(self) -> float:
        if not self.check_in_time or not self.check_out_time:
            return 0.0

        seconds = (self.check_out_time - self.check_in_time).total_seconds()
        return max(0.0, seconds / 3600.0)

    def is_deleted(self) -> bool:
        return self.lifecycle.is_deleted()

    def soft_delete(self, *, actor_id: ObjectId | str) -> None:
        self.lifecycle.soft_delete(actor_id=str(actor_id))
