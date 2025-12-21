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
from app.contexts.school.policies.subject_policy import SubjectPolicy
from app.contexts.school.errors.subject_exceptions import SubjectNotFoundException

def _sess(session: Optional[ClientSession]) -> dict:
    return {"session": session} if session else {}






LC_CREATED_AT = "lifecycle.created_at"
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


def _set_is_active_update(is_active: bool) -> dict:
    n = now_utc()
    return {"$set": {"is_active": bool(is_active), LC_UPDATED_AT: n}}


class SubjectLifecycleService:
    """
    Lifecycle + safety service for Subject.

    Subject is reference data:
    - Deletion is often blocked if referenced (classes/schedules/grades).
    - Prefer deactivate/activate for normal operations.
    """

    def __init__(self, db: Database):
        self.db = db
        self.collection = db.subjects  # adjust if different
        self.policy = SubjectPolicy(db)

    def _deny(self, subject_id: ObjectId, can: PolicyResult) -> None:
        raise LifecyclePolicyDeniedException(
            entity="subject",
            entity_id=str(subject_id),
            mode=can.mode,
            reasons=can.reasons,
            recommended=can.recommended,
        )

    def soft_delete_subject(self, subject_id: ObjectId, actor_id: ObjectId) -> UpdateResult:
        can = self.policy.can_soft_delete(subject_id)
        if not can.allowed:
            self._deny(subject_id, can)

        with mongo_transaction(self.db) as session:
            res = self.collection.update_one(
                {"_id": subject_id, **NOT_DELETED},
                _soft_delete_update(actor_id),
                **_sess(session),
            )
            if res.matched_count == 0:
                raise SubjectNotFoundException(str(subject_id))
            return res

    def restore_subject(self, subject_id: ObjectId) -> UpdateResult:
        can = self.policy.can_restore(subject_id)
        if not can.allowed:
            self._deny(subject_id, can)

        with mongo_transaction(self.db) as session:
            res = self.collection.update_one(
                {"_id": subject_id, **DELETED},
                _restore_update(),
                **_sess(session),
            )
            if res.matched_count == 0:
                raise SubjectNotFoundException(str(subject_id))
            return res

    def set_subject_active(self, subject_id: ObjectId, is_active: bool, *, require_not_deleted: bool = True) -> UpdateResult:
        """
        Business toggle (activate/deactivate). This is usually what you want instead of delete.
        """
        guard: dict = {"_id": subject_id}
        if require_not_deleted:
            guard.update(NOT_DELETED)

        with mongo_transaction(self.db) as session:
            res = self.collection.update_one(
                guard,
                _set_is_active_update(is_active),
                **_sess(session),
            )
            if res.matched_count == 0:
                raise SubjectNotFoundException(str(subject_id))
            return res

    def hard_delete_subject(self, subject_id: ObjectId, actor_id: ObjectId) -> DeleteResult:
        can = self.policy.can_hard_delete(subject_id)
        if not can.allowed:
            self._deny(subject_id, can)

        with mongo_transaction(self.db) as session:
            res = self.collection.delete_one({"_id": subject_id}, **_sess(session))
            if res.deleted_count == 0:
                raise SubjectNotFoundException(str(subject_id))
            return res