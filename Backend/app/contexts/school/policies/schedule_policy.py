
from bson import ObjectId
from pymongo.database import Database

from app.contexts.shared.lifecycle.filters import by_show_deleted, not_deleted
from app.contexts.shared.lifecycle.policy_result import PolicyResult


class SchedulePolicy:
    """
    Rules for ScheduleSlot lifecycle actions.

    Lifecycle consistency:
    - soft delete checks operate on ACTIVE schedule slot (not deleted)
    - optional cross-checks should be lifecycle-aware
    - hard delete / restore checks operate on ANY slot (including deleted)
    """

    def __init__(self, db: Database):
        self.schedules = db["schedules"]
        self.classes = db["classes"]

    def can_soft_delete(self, slot_id: ObjectId) -> PolicyResult:
        slot = self.schedules.find_one(
            not_deleted({"_id": slot_id}),
            {"class_id": 1},
        )
        if not slot:
            return PolicyResult.deny("soft", {"schedule_slot": "not_found_or_deleted"})

        class_id = slot.get("class_id")
        if class_id:
            cls = self.classes.find_one(
                by_show_deleted("all", {"_id": class_id}),
                {"_id": 1, "lifecycle.deleted_at": 1},
            )
            if not cls:
                return PolicyResult.deny("soft", {"class": "not_found"})

        return PolicyResult.ok("soft")

    def can_hard_delete(self, slot_id: ObjectId) -> PolicyResult:
        exists = self.schedules.count_documents(by_show_deleted("all", {"_id": slot_id}), limit=1)
        if exists == 0:
            return PolicyResult.deny("hard", {"schedule_slot": "not_found"})
        return PolicyResult.ok("hard")

    def can_restore(self, slot_id: ObjectId) -> PolicyResult:
        exists = self.schedules.count_documents(by_show_deleted("all", {"_id": slot_id}), limit=1)
        if exists == 0:
            return PolicyResult.deny("restore", {"schedule_slot": "not_found"})
        return PolicyResult.ok("restore")