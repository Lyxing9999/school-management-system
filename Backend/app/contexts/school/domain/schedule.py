# app/contexts/school/domain/schedule.py

from __future__ import annotations
from datetime import datetime, time
from enum import Enum
from bson import ObjectId
from app.contexts.school.errors.schedule_exceptions import (
    InvalidDayOfWeekException,
    InvalidScheduleTimeException,
    StartTimeAfterEndTimeException
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
    Used to detect conflicts for teacher or room.
    """

    def __init__(
        self,
        class_id: ObjectId,
        teacher_id: ObjectId,
        day_of_week: DayOfWeek,
        start_time: time,
        end_time: time,
        id: ObjectId | None = None,
        room: str | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ):
        if not isinstance(class_id, ObjectId):
            class_id = ObjectId(class_id)
        if not isinstance(teacher_id, ObjectId):
            teacher_id = ObjectId(teacher_id)

        self.id = id or ObjectId()
        self.class_id = class_id
        self.teacher_id = teacher_id
        self.day_of_week = self._validate_day(day_of_week)
        self.start_time = self._validate_time(start_time)
        self.end_time = self._validate_time(end_time)
        self._validate_start_before_end()
        self.room = room
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    # -------- Behavior --------

    def move(
        self,
        new_day_of_week: DayOfWeek,
        new_start: time,
        new_end: time,
        new_room: str | None = None,
    ) -> None:
        self.day_of_week = self._validate_day(new_day_of_week)
        self.start_time = self._validate_time(new_start)
        self.end_time = self._validate_time(new_end)
        self._validate_start_before_end()
        if new_room is not None:
            self.room = new_room
        self._touch()

    def overlaps(self, other: "ScheduleSlot") -> bool:
        """
        Check if this slot overlaps with another on the same day.
        (Use in services for teacher/room conflict detection.)
        """
        if self.day_of_week != other.day_of_week:
            return False

        return not (
            self.end_time <= other.start_time
            or other.end_time <= self.start_time
        )

    # -------- Internal helpers --------
    def _touch(self) -> None:
        self.updated_at = datetime.utcnow()

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