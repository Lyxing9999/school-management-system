from __future__ import annotations

from datetime import datetime, date as date_type
from enum import Enum
from bson import ObjectId
from zoneinfo import ZoneInfo

from app.contexts.shared.lifecycle.domain import Lifecycle, now_utc
from app.contexts.school.errors.attendance_exceptions import (
    InvalidAttendanceStatusException,
    AttendanceDateInFutureException,
    AttendanceRecordDeletedException,
)

KH_TZ = ZoneInfo("Asia/Phnom_Penh")


def today_kh() -> date_type:
    return datetime.now(KH_TZ).date()


class AttendanceStatus(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    EXCUSED = "excused"


class AttendanceRecord:
    """
    One attendance mark per (student_id, class_id, date).

    Notes:
    - date is a KH school date (no timezone)
    - lifecycle timestamps are UTC (created_at/updated_at/deleted_at)
    """

    def __init__(
        self,
        student_id: ObjectId | str,
        class_id: ObjectId | str,
        status: AttendanceStatus | str,
        *,
        id: ObjectId | None = None,
        record_date: date_type | None = None,               # KH school day
        marked_by_teacher_id: ObjectId | str | None = None, # teacher IAM id or staff id (your choice)
        lifecycle: Lifecycle | None = None,
    ) -> None:
        self.id = id or ObjectId()
        self.student_id = student_id if isinstance(student_id, ObjectId) else ObjectId(student_id)
        self.class_id = class_id if isinstance(class_id, ObjectId) else ObjectId(class_id)

        self._status = self._validate_status(status)
        self.date = record_date or today_kh()

        self.marked_by_teacher_id = (
            marked_by_teacher_id
            if (marked_by_teacher_id is None or isinstance(marked_by_teacher_id, ObjectId))
            else ObjectId(marked_by_teacher_id)
        )

        self.lifecycle = lifecycle or Lifecycle()

        self._validate_date_not_in_future()

    # -------- Properties --------

    @property
    def status(self) -> AttendanceStatus:
        return self._status

    # -------- Behavior --------

    def change_status(
        self,
        new_status: AttendanceStatus | str,
        *,
        actor_id: ObjectId | None = None,
    ) -> None:
        if self.is_deleted():
            raise AttendanceRecordDeletedException(self.id)

        self._status = self._validate_status(new_status)

        # Optional: capture who changed the mark
        if actor_id is not None:
            self.marked_by_teacher_id = actor_id

        self._touch()

    def soft_delete(self, actor_id: ObjectId) -> None:
        self.lifecycle.soft_delete(actor_id)

    def restore(self) -> None:
        self.lifecycle.restore()

    def is_deleted(self) -> bool:
        return self.lifecycle.is_deleted()

    # -------- Internal helpers --------

    def _touch(self) -> None:
        self.lifecycle.touch(now_utc())

    @staticmethod
    def _validate_status(status: AttendanceStatus | str) -> AttendanceStatus:
        if isinstance(status, AttendanceStatus):
            return status
        try:
            return AttendanceStatus(status)
        except ValueError:
            raise InvalidAttendanceStatusException(status)

    def _validate_date_not_in_future(self) -> None:
        if self.date > today_kh():
            raise AttendanceDateInFutureException(self.date)