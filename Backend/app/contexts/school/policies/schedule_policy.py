from __future__ import annotations

from bson import ObjectId
from pymongo.database import Database

from app.contexts.shared.lifecycle.policy_result import PolicyResult


LIFECYCLE_NOT_DELETED = {"lifecycle.deleted_at": None}


class SchedulePolicy:
    """
    Rules for ScheduleSlot lifecycle actions.
    Most systems allow soft delete freely.
    Hard delete is usually blocked if referenced by audit/history (optional).
    """

    def __init__(self, db: Database):
        self.schedules = db.schedules  
        self.classes = db.classes

    def can_soft_delete(self, slot_id: ObjectId) -> PolicyResult:
        slot = self.schedules.find_one({"_id": slot_id, **LIFECYCLE_NOT_DELETED}, {"class_id": 1})
        if not slot:
            return PolicyResult.deny("soft", {"schedule_slot": "not_found_or_deleted"})

        # Optional rule: block deleting schedule if class itself is deleted
        # (usually you still allow deleting schedule, but choose your rule)
        class_id = slot.get("class_id")
        if class_id:
            cls = self.classes.find_one({"_id": class_id}, {"lifecycle.deleted_at": 1})
            if not cls:
                return PolicyResult.deny("soft", {"class": "not_found"})

        return PolicyResult.ok("soft")

    def can_hard_delete(self, slot_id: ObjectId) -> PolicyResult:
        exists = self.schedules.count_documents({"_id": slot_id})
        if exists == 0:
            return PolicyResult.deny("hard", {"schedule_slot": "not_found"})

        # Usually OK to hard delete schedules if no audit needs.
        return PolicyResult.ok("hard")

    def can_restore(self, slot_id: ObjectId) -> PolicyResult:
        exists = self.schedules.count_documents({"_id": slot_id})
        if exists == 0:
            return PolicyResult.deny("restore", {"schedule_slot": "not_found"})
        return PolicyResult.ok("restore")