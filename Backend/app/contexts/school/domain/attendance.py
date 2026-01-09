# app/contexts/school/domain/attendance.py
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
    Session attendance:
      - one record per student per schedule session (class+subject+slot) per date
    """

    def __init__(
        self,
        student_id: ObjectId | str,
        class_id: ObjectId | str,
        subject_id: ObjectId | str,
        schedule_slot_id: ObjectId | str,
        status: AttendanceStatus | str,
        *,
        id: ObjectId | None = None,
        record_date: date_type | None = None,
        marked_by_teacher_id: ObjectId | str | None = None,
        lifecycle: Lifecycle | None = None,
    ) -> None:
        self.id = id or ObjectId()

        self.student_id = student_id if isinstance(student_id, ObjectId) else ObjectId(student_id)
        self.class_id = class_id if isinstance(class_id, ObjectId) else ObjectId(class_id)
        self.subject_id = subject_id if isinstance(subject_id, ObjectId) else ObjectId(subject_id)
        self.schedule_slot_id = (
            schedule_slot_id if isinstance(schedule_slot_id, ObjectId) else ObjectId(schedule_slot_id)
        )

        self._status = self._validate_status(status)

        # canonical date (KH school date)
        self.record_date = record_date or today_kh()

        self.marked_by_teacher_id = (
            marked_by_teacher_id
            if (marked_by_teacher_id is None or isinstance(marked_by_teacher_id, ObjectId))
            else ObjectId(marked_by_teacher_id)
        )

        self.lifecycle = lifecycle or Lifecycle()
        self._validate_date_not_in_future()

    # ---- backward compatibility alias ----
    @property
    def date(self) -> date_type:
        return self.record_date

    @date.setter
    def date(self, value: date_type) -> None:
        self.record_date = value

    @property
    def status(self) -> AttendanceStatus:
        return self._status

    def change_status(self, new_status: AttendanceStatus | str, *, actor_id: ObjectId | None = None) -> None:
        if self.is_deleted():
            raise AttendanceRecordDeletedException(self.id)

        self._status = self._validate_status(new_status)
        if actor_id is not None:
            self.marked_by_teacher_id = actor_id
        self.lifecycle.touch(now_utc())

    def soft_delete(self, actor_id: ObjectId) -> None:
        self.lifecycle.soft_delete(actor_id)

    def restore(self) -> None:
        self.lifecycle.restore()

    def is_deleted(self) -> bool:
        return self.lifecycle.is_deleted()

    @staticmethod
    def _validate_status(status: AttendanceStatus | str) -> AttendanceStatus:
        if isinstance(status, AttendanceStatus):
            return status
        try:
            return AttendanceStatus(str(status).strip().lower())
        except ValueError:
            raise InvalidAttendanceStatusException(status)

    def _validate_date_not_in_future(self) -> None:
        if self.record_date > today_kh():
            raise AttendanceDateInFutureException(self.record_date)