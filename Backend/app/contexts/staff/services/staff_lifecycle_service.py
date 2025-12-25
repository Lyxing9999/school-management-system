from __future__ import annotations

from typing import Optional
from bson import ObjectId
from pymongo.database import Database
from pymongo.client_session import ClientSession
from pymongo.results import UpdateResult

from app.contexts.shared.lifecycle.transaction import mongo_transaction
from app.contexts.shared.lifecycle.updates import apply_soft_delete_update, apply_restore_update
from app.contexts.shared.lifecycle.errors import LifecyclePolicyDeniedException
from app.contexts.shared.lifecycle.policy_result import PolicyResult

from app.contexts.staff.policies.staff_policy import StaffPolicy
from app.contexts.iam.error.iam_exception import NotFoundUserException
from app.contexts.staff.errors.staff_exceptions import StaffNotFoundException 


def _sess(session: Optional[ClientSession]) -> dict:
    return {"session": session} if session else {}


LIFECYCLE_NOT_DELETED = {"lifecycle.deleted_at": None}
LIFECYCLE_DELETED = {"lifecycle.deleted_at": {"$ne": None}}


class StaffLifecycleService:
    def __init__(self, db: Database):
        self.db = db
        self.staff = db.staff
        self.iam = db.iam
        self.policy = StaffPolicy(db)

    def _deny(self, user_id: ObjectId, can: PolicyResult) -> None:
        raise LifecyclePolicyDeniedException(
            entity="staff_user",
            entity_id=str(user_id),
            mode=can.mode,
            reasons=can.reasons,
            recommended=can.recommended,
        )

    def soft_delete_by_user_id(self, user_id: ObjectId, actor_id: ObjectId) -> UpdateResult:
        can = self.policy.can_soft_delete_user(user_id)
        if not can.allowed:
            self._deny(user_id, can)

        with mongo_transaction(self.db) as session:
            staff_doc = self.staff.find_one(
                {"user_id": user_id, **LIFECYCLE_NOT_DELETED},
                {"_id": 1, "user_id": 1},
                **_sess(session),
            )

            if staff_doc:
                staff_res = self.staff.update_one(
                    {"_id": staff_doc["_id"], **LIFECYCLE_NOT_DELETED},
                    apply_soft_delete_update(actor_id),
                    **_sess(session),
                )
                if staff_res.matched_count == 0:
                    raise StaffNotFoundException(str(user_id))

            iam_res = self.iam.update_one(
                {"_id": user_id, **LIFECYCLE_NOT_DELETED},
                apply_soft_delete_update(actor_id),
                **_sess(session),
            )
            if iam_res.matched_count == 0:
                raise NotFoundUserException(str(user_id))

            return iam_res

    def restore_by_user_id(self, user_id: ObjectId, actor_id: ObjectId) -> UpdateResult:
        can = self.policy.can_restore_user(user_id)
        if not can.allowed:
            self._deny(user_id, can)

        with mongo_transaction(self.db) as session:
            staff_doc = self.staff.find_one(
                {"user_id": user_id, **LIFECYCLE_DELETED},
                {"_id": 1, "user_id": 1},
                **_sess(session),
            )

            if staff_doc:
                staff_res = self.staff.update_one(
                    {"_id": staff_doc["_id"], **LIFECYCLE_DELETED},
                    apply_restore_update(),
                    **_sess(session),
                )
                if staff_res.matched_count == 0:
                    raise StaffNotFoundException(str(user_id))

            iam_res = self.iam.update_one(
                {"_id": user_id, **LIFECYCLE_DELETED},
                apply_restore_update(),
                **_sess(session),
            )
            if iam_res.matched_count == 0:
                raise NotFoundUserException(str(user_id))

            return iam_res