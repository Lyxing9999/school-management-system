# app/contexts/school/mapper/schedule_mapper.py

from datetime import datetime, time
from app.contexts.school.domain.schedule import ScheduleSlot, DayOfWeek


class ScheduleMapper:
    """
    Handles conversion between ScheduleSlot domain model and MongoDB dict.
    """

    @staticmethod
    def to_domain(data: dict | ScheduleSlot) -> ScheduleSlot:
        if isinstance(data, ScheduleSlot):
            return data

        # Parse times from string or time
        start_raw = data["start_time"]
        end_raw = data["end_time"]

        start_time = (
            start_raw
            if isinstance(start_raw, time)
            else datetime.strptime(start_raw, "%H:%M").time()
        )
        end_time = (
            end_raw
            if isinstance(end_raw, time)
            else datetime.strptime(end_raw, "%H:%M").time()
        )

        return ScheduleSlot(
            id=data.get("_id"),
            class_id=data["class_id"],
            teacher_id=data["teacher_id"],
            day_of_week=data.get("day_of_week"),
            start_time=start_time,
            end_time=end_time,
            room=data.get("room"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    @staticmethod
    def to_persistence(slot: ScheduleSlot) -> dict:
        return {
            "_id": slot.id,
            "class_id": slot.class_id,
            "teacher_id": slot.teacher_id,
            "day_of_week": int(slot.day_of_week),
            "start_time": slot.start_time.strftime("%H:%M"),
            "end_time": slot.end_time.strftime("%H:%M"),
            "room": slot.room,
            "created_at": slot.created_at,
            "updated_at": slot.updated_at,
        }