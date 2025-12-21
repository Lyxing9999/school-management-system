from __future__ import annotations

from bson import ObjectId
from pymongo.database import Database

from app.contexts.shared.lifecycle.policy_result import PolicyResult
from app.contexts.shared.lifecycle.types import not_deleted


class StaffPolicy:
    def __init__(self, db: Database):
        self.staff = db.staff
        self.classes = db.classes
        self.schedule = db.schedule  
        
    def _get_staff_by_user_id(self, user_id: ObjectId) -> dict | None:
        return self.staff.find_one(not_deleted({"user_id": user_id}), {"_id": 1})

    # Called when deleting IAM user with role=teacher
    def can_soft_delete_user(self, user_id: ObjectId) -> PolicyResult:
        staff_doc = self._get_staff_by_user_id(user_id)
        if not staff_doc:
            return PolicyResult.ok("soft")

        teacher_id = staff_doc["_id"]
        blockers: dict = {}

        class_count = self.classes.count_documents(not_deleted({"teacher_id": teacher_id}))
        if class_count > 0:
            blockers["assigned_classes"] = class_count

        schedule_count = self.schedule.count_documents(not_deleted({"teacher_id": teacher_id}))
        if schedule_count > 0:
            blockers["schedule_slots"] = schedule_count

        return PolicyResult.deny("soft", blockers) if blockers else PolicyResult.ok("soft")

    def can_hard_delete_user(self, user_id: ObjectId) -> PolicyResult:
        staff_doc = self._get_staff_by_user_id(user_id)
        if not staff_doc:
            return PolicyResult.ok("hard")

        teacher_id = staff_doc["_id"]

        # Hard delete blocked if still referenced
        class_count = self.classes.count_documents(not_deleted({"teacher_id": teacher_id}))
        schedule_count = self.schedule.count_documents(not_deleted({"teacher_id": teacher_id}))

        if class_count > 0 or schedule_count > 0:
            return PolicyResult.deny(
                "hard",
                {"assigned_classes": class_count, "schedule_slots": schedule_count},
                recommended="soft",
            )

        return PolicyResult.ok("hard")

    def can_restore_user(self, user_id: ObjectId) -> PolicyResult:
        exists = self.staff.count_documents({"user_id": user_id})
        if exists == 0:
            return PolicyResult.deny("restore", {"staff": "not_found"})
        return PolicyResult.ok("restore")