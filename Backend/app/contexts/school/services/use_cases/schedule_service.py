from __future__ import annotations

from datetime import time
from bson import ObjectId

from app.contexts.school.domain.schedule import ScheduleSlot, DayOfWeek
from app.contexts.school.errors.class_exceptions import ClassNotFoundException
from app.contexts.school.errors.schedule_exceptions import (
    ScheduleNotFoundException,
    ScheduleUpdateFailedException,
)

from ._base import OidMixin


class ScheduleService(OidMixin):
    def __init__(self, *, schedule_repo, class_repo, schedule_lifecycle):
        self.schedule_repo = schedule_repo
        self.class_repo = class_repo
        self.schedule_lifecycle = schedule_lifecycle

    # ------------------------
    # Create / Update (domain)
    # ------------------------

    def create_schedule_slot_for_class(
        self,
        class_id: str | ObjectId,
        teacher_id: str | ObjectId,
        day_of_week: DayOfWeek | int,
        start_time: time,
        end_time: time,
        room: str | None = None,
    ) -> ScheduleSlot:
        class_oid = self._oid(class_id)
        teacher_oid = self._oid(teacher_id)

        if self.class_repo.find_by_id(class_oid) is None:
            raise ClassNotFoundException(str(class_id))

        slot = ScheduleSlot(
            class_id=class_oid,
            teacher_id=teacher_oid,
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time,
            room=room,
        )
        return self.schedule_repo.insert(slot)

    def move_schedule_slot(
        self,
        slot_id: str | ObjectId,
        new_day_of_week: DayOfWeek | int,
        new_start_time: time,
        new_end_time: time,
        new_room: str | None = None,
    ) -> ScheduleSlot:
        oid = self._oid(slot_id)
        slot = self.schedule_repo.find_by_id(oid)
        if slot is None:
            raise ScheduleNotFoundException(str(slot_id))

        slot.move(
            new_day_of_week=new_day_of_week,
            new_start=new_start_time,
            new_end=new_end_time,
            new_room=new_room,
        )

        updated = self.schedule_repo.update(slot)
        if updated is None:
            raise ScheduleUpdateFailedException(str(slot_id))
        return updated

    # ------------------------
    # Lifecycle operations
    # ------------------------

    def soft_delete_schedule_slot(self, slot_id: str | ObjectId, actor_id: str | ObjectId) -> bool:
        oid = self._oid(slot_id)
        actor_oid = self._oid(actor_id)
        res = self.schedule_lifecycle.soft_delete_slot(oid, actor_oid)
        return res.modified_count > 0

    def restore_schedule_slot(self, slot_id: str | ObjectId) -> bool:
        oid = self._oid(slot_id)
        res = self.schedule_lifecycle.restore_slot(oid)
        return res.modified_count > 0

    def hard_delete_schedule_slot(self, slot_id: str | ObjectId, actor_id: str | ObjectId) -> bool:
        oid = self._oid(slot_id)
        actor_oid = self._oid(actor_id)
        res = self.schedule_lifecycle.hard_delete_slot(oid, actor_oid)
        return res.deleted_count > 0

    # Optional: keep legacy “delete” name if controllers already call it
    def delete_schedule_slot(self, slot_id: str | ObjectId) -> bool:
        return self.schedule_repo.delete(self._oid(slot_id))