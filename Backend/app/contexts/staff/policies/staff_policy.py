from __future__ import annotations

from bson import ObjectId
from pymongo.database import Database

from app.contexts.shared.lifecycle.policy_result import PolicyResult
from app.contexts.shared.lifecycle.filters import not_deleted


LIFECYCLE_DELETED = {"lifecycle.deleted_at": {"$exists": True, "$ne": None}}


class StaffPolicy:
    def __init__(self, db: Database):
        self.staff = db.staff
        self.class_sections = db.classes
        self.schedule_slots = db.schedule
    def _get_active_staff_by_user_id(self, user_id: ObjectId) -> dict | None:
        return self.staff.find_one(not_deleted({"user_id": user_id}), {"_id": 1})

    def can_soft_delete_user(self, user_id: ObjectId) -> PolicyResult:
        staff_doc = self._get_active_staff_by_user_id(user_id)
        if not staff_doc:
            return PolicyResult.ok("soft")

        teacher_id = staff_doc["_id"]
        blockers: dict = {}

        class_count = self.class_sections.count_documents(not_deleted({"teacher_id": teacher_id}))
        if class_count:
            blockers["assigned_classes"] = class_count

        schedule_count = self.schedule_slots.count_documents(not_deleted({"teacher_id": teacher_id}))
        if schedule_count:
            blockers["schedule_slots"] = schedule_count

        return PolicyResult.deny("soft", blockers) if blockers else PolicyResult.ok("soft")

    def can_hard_delete_user(self, user_id: ObjectId) -> PolicyResult:
        staff_doc = self._get_active_staff_by_user_id(user_id)
        if not staff_doc:
            return PolicyResult.ok("hard")

        teacher_id = staff_doc["_id"]

        class_count = self.class_sections.count_documents(not_deleted({"teacher_id": teacher_id}))
        schedule_count = self.schedule_slots.count_documents(not_deleted({"teacher_id": teacher_id}))

        if class_count or schedule_count:
            return PolicyResult.deny(
                "hard",
                {"assigned_classes": class_count, "schedule_slots": schedule_count},
                recommended="soft",
            )

        return PolicyResult.ok("hard")

    def can_restore_user(self, user_id: ObjectId) -> PolicyResult:
        deleted_exists = self.staff.count_documents({"user_id": user_id, **LIFECYCLE_DELETED})
        if deleted_exists == 0:
            return PolicyResult.deny("restore", {"staff": "not_found_or_not_deleted"})
        return PolicyResult.ok("restore")