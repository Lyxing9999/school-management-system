from __future__ import annotations
from datetime import datetime, date as date_type
from enum import Enum
from bson import ObjectId

from zoneinfo import ZoneInfo

KH_TZ = ZoneInfo("Asia/Phnom_Penh")


from app.contexts.school.errors.attendance_exceptions import (
    InvalidAttendanceStatusException,
    AttendanceDateInFutureException,
)


class AttendanceStatus(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    EXCUSED = "excused"


class AttendanceRecord:
    """
    Represents a single attendance mark for a given student + class + date.
    """

    def __init__(
        self,
        student_id: ObjectId,
        class_id: ObjectId,
        status: AttendanceStatus | str,
        id: ObjectId | None = None,
        record_date: date_type | None = None,
        marked_by_teacher_id: ObjectId | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ):
        # Normalize ObjectIds
        if not isinstance(student_id, ObjectId):
            student_id = ObjectId(student_id)
        if not isinstance(class_id, ObjectId):
            class_id = ObjectId(class_id)

        self.id = id or ObjectId()
        self.student_id = student_id
        self.class_id = class_id
        self._status = self._validate_status(status)
        self.date = record_date or datetime.now(KH_TZ).date()
        self.marked_by_teacher_id = marked_by_teacher_id
        self.created_at = created_at or datetime.now(KH_TZ)
        self.updated_at = updated_at or datetime.now(KH_TZ)

        # Validate business rules
        self._validate_date_not_too_far_future()

    # -------- Properties --------

    @property
    def status(self) -> AttendanceStatus:
        return self._status

    # -------- Behavior --------

    def change_status(self, new_status: AttendanceStatus | str) -> None:
        self._status = self._validate_status(new_status)
        self._touch()

    # -------- Internal helpers --------

    def _touch(self) -> None:
        self.updated_at = datetime.now(KH_TZ)

    @staticmethod
    def _validate_status(status: AttendanceStatus | str) -> AttendanceStatus:
        """Validate attendance status and raise domain-specific exception if invalid."""
        if isinstance(status, AttendanceStatus):
            return status
        try:
            return AttendanceStatus(status)
        except ValueError:
            raise InvalidAttendanceStatusException(status)

    def _validate_date_not_too_far_future(self) -> None:
        """Raise domain-specific exception if date is in the future."""
        today = datetime.now(KH_TZ).date()
        if self.date > today:
            raise AttendanceDateInFutureException(self.date)
