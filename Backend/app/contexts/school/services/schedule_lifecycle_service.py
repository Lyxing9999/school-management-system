from __future__ import annotations

from typing import Optional
from bson import ObjectId
from pymongo.database import Database
from pymongo.client_session import ClientSession
from pymongo.results import UpdateResult, DeleteResult

from app.contexts.shared.lifecycle.transaction import mongo_transaction
from app.contexts.shared.lifecycle.policy_result import PolicyResult
from app.contexts.shared.lifecycle.errors import LifecyclePolicyDeniedException
from app.contexts.shared.lifecycle.domain import now_utc 

from app.contexts.school.policies.schedule_policy import SchedulePolicy
from app.contexts.school.errors.schedule_exceptions import ScheduleNotFoundException  


def _sess(session: Optional[ClientSession]) -> dict:
    return {"session": session} if session else {}



LC_UPDATED_AT = "lifecycle.updated_at"
LC_DELETED_AT = "lifecycle.deleted_at"
LC_DELETED_BY = "lifecycle.deleted_by"

NOT_DELETED = {LC_DELETED_AT: None}
DELETED = {LC_DELETED_AT: {"$ne": None}}


def _soft_delete_update(actor_id: ObjectId) -> dict:
    n = now_utc()
    return {"$set": {LC_DELETED_AT: n, LC_DELETED_BY: actor_id, LC_UPDATED_AT: n}}


def _restore_update() -> dict:
    n = now_utc()
    return {"$set": {LC_DELETED_AT: None, LC_DELETED_BY: None, LC_UPDATED_AT: n}}


class ScheduleLifecycleService:
    """
    Lifecycle + safety service for ScheduleSlot.

    Usually safe to soft-delete schedule slots freely.
    Policy can enforce constraints if you want (e.g. class must exist).
    """

    def __init__(self, db: Database):
        self.db = db
        self.collection = db.schedules  # if yours is db.schedule, change here
        self.policy = SchedulePolicy(db)

    def _deny(self, slot_id: ObjectId, can: PolicyResult) -> None:
        raise LifecyclePolicyDeniedException(
            entity="schedule_slot",
            entity_id=str(slot_id),
            mode=can.mode,
            reasons=can.reasons,
            recommended=can.recommended,
        )

    def soft_delete_slot(self, slot_id: ObjectId, actor_id: ObjectId) -> UpdateResult:
        can = self.policy.can_soft_delete(slot_id)
        if not can.allowed:
            self._deny(slot_id, can)

        with mongo_transaction(self.db) as session:
            res = self.collection.update_one(
                {"_id": slot_id, **NOT_DELETED},
                _soft_delete_update(actor_id),
                **_sess(session),
            )
            if res.matched_count == 0:
                raise ScheduleNotFoundException(str(slot_id))
            return res

    def restore_slot(self, slot_id: ObjectId) -> UpdateResult:
        can = self.policy.can_restore(slot_id)
        if not can.allowed:
            self._deny(slot_id, can)

        with mongo_transaction(self.db) as session:
            res = self.collection.update_one(
                {"_id": slot_id, **DELETED},
                _restore_update(),
                **_sess(session),
            )
            if res.matched_count == 0:
                raise ScheduleNotFoundException(str(slot_id))
            return res

    def hard_delete_slot(self, slot_id: ObjectId, actor_id: ObjectId) -> DeleteResult:
        can = self.policy.can_hard_delete(slot_id)
        if not can.allowed:
            self._deny(slot_id, can)

        with mongo_transaction(self.db) as session:
            res = self.collection.delete_one({"_id": slot_id}, **_sess(session))
            if res.deleted_count == 0:
                raise ScheduleNotFoundException(str(slot_id))
            return res