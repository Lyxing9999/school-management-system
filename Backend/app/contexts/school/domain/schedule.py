from __future__ import annotations

from datetime import time
from enum import Enum
from bson import ObjectId

from app.contexts.shared.lifecycle.domain import Lifecycle, now_utc
from app.contexts.school.errors.schedule_exceptions import (
    InvalidDayOfWeekException,
    InvalidScheduleTimeException,
    StartTimeAfterEndTimeException,
    ScheduleSlotDeletedException,  # add this
)


class DayOfWeek(int, Enum):
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7


class ScheduleSlot:
    """
    Represents a single scheduled time slot for a class.

    Notes:
    - lifecycle timestamps are UTC
    - soft delete supported (recommended for audit + undo)
    """

    def __init__(
        self,
        class_id: ObjectId | str,
        teacher_id: ObjectId | str,
        day_of_week: DayOfWeek | int,
        start_time: time,
        end_time: time,
        *,
        id: ObjectId | None = None,
        room: str | None = None,
        subject_id: ObjectId | str | None = None,  # optional but often useful
        lifecycle: Lifecycle | None = None,
    ) -> None:
        self.id = id or ObjectId()
        self.class_id = class_id if isinstance(class_id, ObjectId) else ObjectId(class_id)
        self.teacher_id = teacher_id if isinstance(teacher_id, ObjectId) else ObjectId(teacher_id)
        self.subject_id = subject_id if (subject_id is None or isinstance(subject_id, ObjectId)) else ObjectId(subject_id)

        self.day_of_week = self._validate_day(day_of_week)
        self.start_time = self._validate_time(start_time)
        self.end_time = self._validate_time(end_time)
        self.room = room

        self.lifecycle = lifecycle or Lifecycle()

        self._validate_start_before_end()

    # -------- Lifecycle helpers --------

    def is_deleted(self) -> bool:
        return self.lifecycle.is_deleted()

    def soft_delete(self, actor_id: ObjectId) -> None:
        self.lifecycle.soft_delete(actor_id)

    def restore(self) -> None:
        self.lifecycle.restore()

    # -------- Behavior --------

    def move(
        self,
        new_day_of_week: DayOfWeek | int,
        new_start: time,
        new_end: time,
        *,
        new_room: str | None = None,
        new_teacher_id: ObjectId | str | None = None,
        new_subject_id: ObjectId | str | None = None,
    ) -> None:
        if self.is_deleted():
            raise ScheduleSlotDeletedException(self.id)

        self.day_of_week = self._validate_day(new_day_of_week)
        self.start_time = self._validate_time(new_start)
        self.end_time = self._validate_time(new_end)
        self._validate_start_before_end()

        if new_room is not None:
            self.room = new_room

        if new_teacher_id is not None:
            self.teacher_id = new_teacher_id if isinstance(new_teacher_id, ObjectId) else ObjectId(new_teacher_id)

        if new_subject_id is not None:
            self.subject_id = new_subject_id if isinstance(new_subject_id, ObjectId) else ObjectId(new_subject_id)

        self._touch()

    def overlaps(self, other: "ScheduleSlot") -> bool:
        """Check overlap on same day (used by service for conflict detection)."""
        if self.day_of_week != other.day_of_week:
            return False

        return not (
            self.end_time <= other.start_time
            or other.end_time <= self.start_time
        )

    # -------- Internal helpers --------

    def _touch(self) -> None:
        self.lifecycle.touch(now_utc())

    @staticmethod
    def _validate_day(day: DayOfWeek | int) -> DayOfWeek:
        if isinstance(day, DayOfWeek):
            return day
        try:
            return DayOfWeek(day)
        except ValueError:
            raise InvalidDayOfWeekException(received_value=day)

    @staticmethod
    def _validate_time(t: time) -> time:
        if not isinstance(t, time):
            raise InvalidScheduleTimeException()
        return t

    def _validate_start_before_end(self) -> None:
        if self.start_time >= self.end_time:
            raise StartTimeAfterEndTimeException(self.start_time, self.end_time)