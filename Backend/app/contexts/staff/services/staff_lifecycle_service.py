from __future__ import annotations
from bson import ObjectId
from pymongo.database import Database
from contexts.shared.lifecycle.types import apply_soft_delete_update, apply_restore_update
from contexts.shared.lifecycle.audit import append_history
from contexts.staff.policies.staff_policy import StaffPolicy


class StaffLifecycleService:
    def __init__(self, db: Database):
        self.db = db
        self.staff = db.staff
        self.users = db.users
        self.policy = StaffPolicy(db)

    def soft_delete_teacher(self, staff_id: ObjectId, actor_id: ObjectId) -> None:
        can = self.policy.can_soft_delete_teacher(staff_id)
        if not can.allowed:
            raise Exception(f"Cannot delete teacher: {can.reasons}")

        doc = self.staff.find_one({"_id": staff_id})
        if not doc:
            return

        self.staff.update_one({"_id": staff_id}, apply_soft_delete_update(actor_id))
        self.users.update_one({"_id": doc["user_id"]}, apply_soft_delete_update(actor_id))
        append_history(self.staff, staff_id, "STAFF_SOFT_DELETED", actor_id)

    def restore_teacher(self, staff_id: ObjectId, actor_id: ObjectId) -> None:
        doc = self.staff.find_one({"_id": staff_id})
        if not doc:
            return

        self.staff.update_one({"_id": staff_id}, apply_restore_update(actor_id))
        self.users.update_one({"_id": doc["user_id"]}, apply_restore_update(actor_id))
        append_history(self.staff, staff_id, "STAFF_RESTORED", actor_id)