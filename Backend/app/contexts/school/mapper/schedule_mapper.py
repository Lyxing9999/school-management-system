from __future__ import annotations

from datetime import datetime, time
from app.contexts.school.domain.schedule import ScheduleSlot
from app.contexts.shared.lifecycle.domain import Lifecycle


class ScheduleMapper:
    @staticmethod
    def to_domain(data: dict | ScheduleSlot) -> ScheduleSlot:
        if isinstance(data, ScheduleSlot):
            return data

        start_raw = data["start_time"]
        end_raw = data["end_time"]

        start_time = start_raw if isinstance(start_raw, time) else datetime.strptime(start_raw, "%H:%M").time()
        end_time = end_raw if isinstance(end_raw, time) else datetime.strptime(end_raw, "%H:%M").time()

        lc_raw = data.get("lifecycle") or {}
        lifecycle = Lifecycle(
            created_at=lc_raw.get("created_at"),
            updated_at=lc_raw.get("updated_at"),
            deleted_at=lc_raw.get("deleted_at"),
            deleted_by=lc_raw.get("deleted_by"),
        )

        return ScheduleSlot(
            id=data.get("_id"),
            class_id=data["class_id"],
            teacher_id=data["teacher_id"],
            day_of_week=data.get("day_of_week"),
            start_time=start_time,
            end_time=end_time,
            room=data.get("room"),
            subject_id=data.get("subject_id"),
            lifecycle=lifecycle,
        )

    @staticmethod
    def to_persistence(slot: ScheduleSlot) -> dict:
        lc = slot.lifecycle
        return {
            "_id": slot.id,
            "class_id": slot.class_id,
            "teacher_id": slot.teacher_id,
            "subject_id": getattr(slot, "subject_id", None),
            "day_of_week": int(slot.day_of_week),
            "start_time": slot.start_time.strftime("%H:%M"),
            "end_time": slot.end_time.strftime("%H:%M"),
            "room": slot.room,
            "lifecycle": {
                "created_at": lc.created_at,
                "updated_at": lc.updated_at,
                "deleted_at": lc.deleted_at,
                "deleted_by": lc.deleted_by,
            },
        }