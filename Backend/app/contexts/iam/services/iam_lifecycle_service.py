from __future__ import annotations
from bson import ObjectId
from pymongo.database import Database
from pymongo.results import UpdateResult, DeleteResult
from app.contexts.shared.lifecycle.types import (
    apply_soft_delete_update, apply_restore_update, apply_set_status_update, Status
)
from app.contexts.iam.policies.iam_policy import IAMPolicy
from app.contexts.iam.error.iam_exception import NotFoundUserException

class IAMLifecycleService:
    def __init__(self, db: Database):
        self.collection = db.iam
        self.policy = IAMPolicy(db)

    def soft_delete_user(self, user_id: ObjectId, actor_id: ObjectId) -> UpdateResult:
        res = self.collection.update_one(
            {"_id": user_id, "deleted": {"$ne": True}},
            apply_soft_delete_update(actor_id),
        )
        if res.matched_count == 0:
            raise NotFoundUserException(str(user_id))
        return res

    def restore_user(self, user_id: ObjectId, actor_id: ObjectId) -> UpdateResult:
        res = self.collection.update_one(
            {"_id": user_id, "deleted": True},
            apply_restore_update(actor_id),
        )
        if res.matched_count == 0:
            raise NotFoundUserException(str(user_id))
        return res

    def set_user_status(self, user_id: ObjectId, status: Status) -> UpdateResult:
        res = self.collection.update_one(
            {"_id": user_id, "deleted": {"$ne": True}},
            apply_set_status_update(status),
        )
        if res.matched_count == 0:
            raise NotFoundUserException(str(user_id))
        return res

    def hard_delete_user(self, user_id: ObjectId) -> DeleteResult:
        can = self.policy.can_hard_delete_user(user_id)
        if not can.allowed:
            # replace with your structured exception
            raise Exception(f"Cannot hard delete user: {can.reasons}")
        return self.collection.delete_one({"_id": user_id})