from __future__ import annotations
from bson import ObjectId
from pymongo.database import Database
from contexts.shared.lifecycle.policy_result import PolicyResult


class StaffPolicy:
    def __init__(self, db: Database):
        self.staff = db.staff
        self.classes = db.classes
        self.schedules = db.schedules  # adjust name if yours is schedule

    def can_soft_delete_teacher(self, staff_id: ObjectId) -> PolicyResult:
        staff_doc = self.staff.find_one({"_id": staff_id})
        if not staff_doc:
            return PolicyResult.deny("soft", {"staff": "not_found"})

        # If teacher owns classes/schedules => block
        class_count = self.classes.count_documents({"teacher_id": staff_id, "deleted": {"$ne": True}})
        sched_count = self.schedules.count_documents({"teacher_id": staff_id})
        if class_count > 0 or sched_count > 0:
            return PolicyResult.deny("soft", {"classes": class_count, "schedules": sched_count})
        return PolicyResult.ok("soft")