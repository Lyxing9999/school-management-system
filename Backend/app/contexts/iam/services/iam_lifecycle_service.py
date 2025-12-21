from __future__ import annotations

from typing import Optional
from bson import ObjectId
from pymongo.database import Database
from pymongo.client_session import ClientSession
from pymongo.results import UpdateResult, DeleteResult

from app.contexts.shared.lifecycle.types import (
    apply_soft_delete_update,
    apply_restore_update,
)
from app.contexts.iam.policies.iam_policy import IAMPolicy
from app.contexts.iam.error.iam_exception import NotFoundUserException
from app.contexts.shared.lifecycle.policy_result import PolicyResult
from app.contexts.shared.lifecycle.errors import LifecyclePolicyDeniedException 
from app.contexts.shared.lifecycle.transaction import mongo_transaction  


def _sess(session: Optional[ClientSession]) -> dict:
    """Pass session only when transactions are supported."""
    return {"session": session} if session else {}


LIFECYCLE_NOT_DELETED = {"lifecycle.deleted_at": None}
LIFECYCLE_DELETED = {"lifecycle.deleted_at": {"$ne": None}}


class IAMLifecycleService:
    def __init__(self, db: Database):
        self.db = db
        self.collection = db.iam
        self.policy = IAMPolicy(db)

    def _deny(self, user_id: ObjectId, can: PolicyResult) -> None:
        raise LifecyclePolicyDeniedException(
            entity="user",
            entity_id=str(user_id),
            mode=can.mode,
            reasons=can.reasons,
            recommended=can.recommended,
        )

    def soft_delete_user(self, user_id: ObjectId, actor_id: ObjectId) -> UpdateResult:
        can = self.policy.can_soft_delete_user(user_id)
        if not can.allowed:
            self._deny(user_id, can)

        with mongo_transaction(self.db) as session:
            res = self.collection.update_one(
                {"_id": user_id, **LIFECYCLE_NOT_DELETED},
                apply_soft_delete_update(actor_id),
                **_sess(session),
            )
            if res.matched_count == 0:
                raise NotFoundUserException(str(user_id))
            return res

    def restore_user(self, user_id: ObjectId, actor_id: ObjectId) -> UpdateResult:
        # optional: add policy.can_restore_user(...) later if you need blockers
        with mongo_transaction(self.db) as session:
            res = self.collection.update_one(
                {"_id": user_id, **LIFECYCLE_DELETED},
                apply_restore_update(actor_id),
                **_sess(session),
            )
            if res.matched_count == 0:
                raise NotFoundUserException(str(user_id))
            return res


    def hard_delete_user(self, user_id: ObjectId, actor_id: ObjectId) -> DeleteResult:
        can = self.policy.can_hard_delete_user(user_id)
        if not can.allowed:
            self._deny(user_id, can)

        with mongo_transaction(self.db) as session:
            # Usually hard-delete should target an already soft-deleted user,
            # but that is a business rule. If you want it, enforce it here:
            # {"_id": user_id, **LIFECYCLE_DELETED}
            return self.collection.delete_one({"_id": user_id, **LIFECYCLE_DELETED}, **_sess(session))